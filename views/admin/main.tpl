{% extends "base.tpl" %}
{% block body %}
<div class="span2 text-center">
    <ul class="blog-admin-nav left-indent nav nav-tabs nav-stacked">
        <li class="nav-header">Blog</li>
        <li><a href='/admin'>Blog Settings</a></li>
        <li class="nav-header">Posts</li>
        <li><a href='/admin/new-post'>New Post</a></li>
        <li><a href='/admin/manage-posts'>Manage Posts</a></li>
        <li class="nav-header">Comments</li>
        <li><a href='/admin/comment-approver'>Comment Manager</a></li>
        <li class="nav-header">Users</li>
        <li><a>My Profile</a></li>
        <li><a>User Management</a></li>
    </ul>
</div>
<div class="span10">
    {% block admin %}
    Stuff
    {% endblock %}
</div>
{% endblock %}