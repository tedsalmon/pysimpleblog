{% extends "admin/main.tpl" %}
{% block admin %}
<header>
    <hgroup>
        <h2>Link Manager</h2>
    </hgroup>
</header>
<hr />
{% if links %}
<table class="table table-condensed table-striped table-hover">
    <thead>
        <tr>
            <th>Title</th>
            <th>URL</th>
            <th>Author</th>
            <th>Delete</th>
        </tr>
    </thead>
    <tbody>
{% for link in links %}
    <tr data-link-id="{{link['_id']}}">
        <td><h title="Click to edit" class="edit-link editable link-title" data-name="title" data-type="text">{{link['title']}}</h></td>
        <td><h title="Click to edit" class="edit-link editable link-url" data-name="url" data-type="text">{{link['url']}}</h></td>
        <td>{{link['author']}}</td>
        <td><a title="Delete Link" class="delete-link icon-ban-circle" href="#"></a></td>
    </tr>
{% endfor %}
    </tbody>
</table>
{% else %}
<h3>No Links found</h3>
{% endif %}
<h4>New Link</h4>
<form class="form-inline">
    <input id='link_title' type="text" placeholder="Link Text">
    <input id='link_url' type="text" placeholder="URL">
    <button id='link_add' type="submit" class="btn">Add Link</button>
</form>
{% endblock %}