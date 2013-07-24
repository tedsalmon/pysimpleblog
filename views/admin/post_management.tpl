{% extends "admin/main.tpl" %}
{% block admin %}
<table class="table table-condensed">
    <thead>
        <tr>
            <th>Title</th>
            <th>URL</th>
            <th>Author</th>
            <th>Created</th>
            <th>Status</th>
            <th>Type</th>
            <th>Edit</th>
            <th>Delete</th>
        </tr>
    </thead>
    <tbody>
{% for post in posts %}
    <tr>
        <td>{{post['title']}}</td>
        <td>{{post['url']}}</td>
        <td>{{post['author']}}</td>
        <td>{{post['date'].strftime('%Y-%m-%d %H:%M:%S')}}</td>
        <td>{% if post['status'] %}Published{% else %}Draft{%endif%}</td>
        <td>{% if post['type'] %}Page{% else %}Post{%endif%}</td>
        <td><a title="Edit Post" class="icon-edit" href="/admin/post-editor/{{post['_id']}}"></a></td>
        <td><a title="Delete Post" class="delete-post icon-ban-circle" href="#" data-post-id="{{post['_id']}}"></a></td>
    </tr>
{% endfor %}
    </tbody>
</table>
{% endblock %}