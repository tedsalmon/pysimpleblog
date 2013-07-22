{% extends "admin/main.tpl" %}
{% block admin %}
<form class="form left-indent" action="#">
    <div class="control-group">
	<div class="controls">
	    <input id="profile_name" class="longer" type="text" placeholder="Display Name" {% if profile_data %}value="{{profile_data['display_name']}}"{% endif %} />
	</div>
    </div>
    <div class="control-group">
	<div class="controls">
	    <button id="update_btn" type="button" class="btn">Update Profile</button>
	    <button id="password_update" type="button" class="btn">Change Password</button>
	</div>
    </div>
    <div class="control-group">
	<div class="controls">
	    <span id="profile_output" class="alert hide in"></span>
	</div>
    </div>
</form>
<div id="password_update_form" class="modal hide fade">
    <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h3>Update Password</h3>
    </div>
    <div class="modal-body">
        <form class="form text-center" action="#">
            <div class="control-group">
                <div class="controls">
                    <input id="password_old" type="text" placeholder="Current Password" />
                </div>
            </div>
            <div class="control-group">
                <div class="controls">
                    <input id="password_new" type="text" placeholder="New Password" />
                </div>
            </div>
            <div class="control-group">
                <div class="controls">
                    <input id="password_confirm" type="text" placeholder="Confirm New Password" />
                </div>
            </div>
            <div class="control-group">
                <div class="controls">
                    <button id="update_password_btn" type="button" class="btn">Change Password</button>
                </div>
            </div>
        </form>
    </div>
</div>
{% endblock %}