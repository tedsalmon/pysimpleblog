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
<input id="link_add_trigger" type="button" class="btn" value="New Link"/>
<div id="link_add_modal" class="modal hide fade">
    <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h4>Add Link</h4>
    </div>
    <div class="modal-body">
        <form class="form-horizontal">
            <div class="control-group">
                <label class="control-label" for="link_title">Link Text</label>
                <div class="controls">
                    <input id='link_title' type="text" placeholder="Link Text">
                </div>
            </div>
            <div class="control-group">
                <label class="control-label" for="link_url">URL</label>
                <div class="controls">
                    <input id='link_url' type="text" placeholder="URL">
                </div>
            </div>
            <div class="control-group">
                <div class="controls">
                    <button id="link_add" type="submit" class="btn" data-dismiss="modal">Add</button>
                </div>
            </div>
        </form>
    </div>
</div>
{% endblock %}