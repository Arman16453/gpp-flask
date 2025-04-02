from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models.result import Result
from app.models.user import User
from app.models.ssip import SSIP
from app import db

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    return redirect(url_for('main.dashboard'))

@bp.route('/dashboard/')
@login_required
def dashboard():
    if current_user.has_role('admin'):
        # Get stats for admin dashboard
        stats = {
            'students': User.query.filter(User.roles.any(name='student')).count(),
            'total_results': Result.query.count(),
            'recent_results': Result.query.order_by(Result.declaration_date.desc()).limit(5).all()
        }
        return render_template('dashboard/admin.html', stats=stats)
    elif current_user.has_role('student'):
        # Get latest result for the student
        latest_result = Result.query.filter_by(
            student_id=current_user.student_id
        ).order_by(Result.declaration_date.desc()).first()
        
        return render_template('dashboard/student.html', latest_result=latest_result)
    else:
        return render_template('dashboard/default.html')

@bp.route('/dashboard/ssip')
@login_required
def ssip_dashboard():
    # Get all SSIP projects
    ssips = SSIP.query.order_by(SSIP.created_at.desc()).all()
    return render_template('dashboard/ssip.html', ssips=ssips)

@bp.route('/dashboard/ssip/apply')
@login_required
def apply_ssip():
    if not current_user.has_role('student'):
        flash('Only students can apply for SSIP projects.', 'error')
        return redirect(url_for('main.ssip_dashboard'))
    return render_template('dashboard/ssip_apply.html')

@bp.route('/dashboard/ssip/submit', methods=['POST'])
@login_required
def submit_ssip_application():
    if not current_user.has_role('student'):
        flash('Only students can apply for SSIP projects.', 'error')
        return redirect(url_for('main.ssip_dashboard'))
    
    # Get form data
    title = request.form.get('title')
    project_type = request.form.get('project_type')
    fund_required = request.form.get('fund_required')
    objective = request.form.get('objective')
    description = request.form.get('description')
    methodology = request.form.get('methodology')
    expected_outcome = request.form.get('expected_outcome')
    
    # Validate required fields
    if not all([title, project_type, fund_required, objective, description, methodology, expected_outcome]):
        flash('All fields are required.', 'error')
        return redirect(url_for('main.apply_ssip'))
    
    try:
        fund_required = float(fund_required)
        if fund_required <= 0:
            raise ValueError('Fund required must be greater than 0')
    except ValueError:
        flash('Invalid fund amount.', 'error')
        return redirect(url_for('main.apply_ssip'))
    
    # Create new SSIP application
    ssip = SSIP(
        title=title,
        project_type=project_type,
        fund_required=fund_required,
        objective=objective,
        description=description,
        methodology=methodology,
        expected_outcome=expected_outcome,
        student_id=current_user.id,
        status='pending'
    )
    
    try:
        db.session.add(ssip)
        db.session.commit()
        flash('Your SSIP application has been submitted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while submitting your application. Please try again.', 'error')
    
    return redirect(url_for('main.ssip_dashboard'))
