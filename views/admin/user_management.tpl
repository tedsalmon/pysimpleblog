{% extends "admin/main.tpl" %}
{% block admin %}
<header>
    <hgroup>
        <h2>User Manager</h2>
    </hgroup>
</header>
<hr />
{% if users %}
<table class="table table-condensed table-striped table-hover">
    <thead>
        <tr>
            <th>Username</th>
            <th>Display Name</th>
            <th>Email Address</th>
            <th>Access Level</th>
            <th>Delete</th>
        </tr>
    </thead>
    <tbody>
{% for user in users %}
    <tr data-link-id="{{user['_id']}}">
        <td>{{user['_id']}}</td>
        <td><h title="Click to edit" class="edit-user editable" data-name="display_name" data-type="text">{{user['display_name']}}</h></td>
        <td><h title="Click to edit" class="edit-user editable" data-name="email_address" data-type="text">{{user['email_address']}}</h></td>
        <td><h title="Click to edit" class="edit-settings-bool editable" data-name="access_level" data-type="select" data-value={{user['access_level']|int}} data-source="[{value: 1, text: 'Editor'},{value: 2, text: 'Admin'}]">{{user['access_name']}}</h></td>
        <td><a title="Delete Link" class="delete-user icon-ban-circle" href="#"></a></td>
    </tr>
{% endfor %}
    </tbody>
</table>
{% else %}
<h3>No Users found</h3>
{% endif %}
<input id="user_add_trigger" type="button" class="btn" value="New User"/>
<div id="user_add_modal" class="modal hide fade">
    <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h4>Add User</h4>
    </div>
    <div class="modal-body">
        <form class="form-horizontal">
            <div class="control-group">
                <label class="control-label" for="user_username">Username</label>
                <div class="controls">
                    <input id='user_username' type="text" placeholder="Username">
                </div>
            </div>
            <div class="control-group">
                <label class="control-label" for="link_url">Display Name</label>
                <div class="controls">
                    <input id='link_url' type="text" placeholder="Display Name">
                </div>
            </div>
            <div class="control-group">
                <label class="control-label" for="user_email_address">Email Address</label>
                <div class="controls">
                    <input id='user_email_address' type="text" placeholder="Email Address">
                </div>
            </div>
            <div class="control-group">
                <label class="control-label" for="user_email_address">Access Level</label>
                <div class="controls">
                    <select id='user_access_level' placeholder="Email Address">
                        <option value="1">Editor</option>
                        <option value="2">Administrator</option>
                    </select>
                </div>
            </div>
            <div class="control-group">
                <label class="control-label" for="user_password">Password</label>
                <div class="controls">
                    <input id='user_password' type="password" placeholder="Password">
                </div>
            </div>
            <div class="control-group">
                <label class="control-label" for="user_password">Confirm</label>
                <div class="controls">
                    <input id='user_password_confirm' type="password" placeholder="Confirm Password">
                </div>
            </div>
            <div class="control-group">
                <div class="controls">
                    <button id="user_add" type="submit" class="btn" data-dismiss="modal">Add</button>
                </div>
            </div>
        </form>
    </div>
</div>
{% endblock %}