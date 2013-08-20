<li class="nav-header">Blog</li>
<li><a href='/admin'>Admin Home</a></li>
{% if 4 in access_level %}
<li><a href='/admin/manage-settings'>Blog Settings</a></li>
{% endif %}
{% if 1 in access_level %}
<li class="nav-header">Posts</li>
<li><a href='/admin/new-post'>New Post</a></li>
<li><a href='/admin/manage-posts'>Post Manager</a></li>
{% endif %}
{% if 2 in access_level %}
<li class="nav-header">Comments</li>
<li><a href='/admin/comment-approver'>Comment Manager</a></li>
{% endif %}
{% if 3 in access_level %}
<li class="nav-header">Navbar Links</li>
<li><a href='/admin/manage-links'>Link Manager</a></li>
{% endif %}
<li class="nav-header">Users</li>
<li><a href="/admin/view-profile">My Profile</a></li>
{% if 5 in access_level %}
<li><a href="/admin/manage-users">User Manager</a></li>
{% endif %}