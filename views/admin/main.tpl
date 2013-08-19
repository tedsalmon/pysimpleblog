{% extends "base.tpl" %}
{% block body %}
<div class="span2 blog-page blog-admin-nav-container">
    <ul class="nav nav-list well blog-admin-nav">
        {% include 'admin/admin_links.tpl' %}
    </ul>
</div>
<div class="blog-content span10">
    {% block admin %}
    {% set types = {0: 'Blog Post', 1: 'Page' } %}
    {% set statuses = {0: 'Draft', 1: 'Published' } %}
    <span class="span6">
        <h4>Overview</h4>
        <a class="muted" href="/admin/comment-approver">Pending Comments: {{comment_count}}</a>
    </span>
    <span class="span6">
        <h4>Quick Blog Post</h4>
        <form class="form">
            <div class="control-group">
                <div class="controls">
                    <input id="entry_title" class="longest" type="text" placeholder="Title..." />
                </div>
            </div>
            <div class="control-group">
                <div class="controls">
                    <textarea class="blog-post-textarea-small" id="entry_body" placeholder="Post content"></textarea>
                </div>
            </div>
            <div class="control-group">
                <div class="controls">
                    <label for="entry_status">Publishing Status</label>
                    <select id="entry_status">
                        {% for status in statuses %}
                        <option value="{{status}}">{{statuses[status]}}</option>
                        {% endfor %}
                    </select>
                    <select id="entry_type" class="hide">
                        <option value="{{type}}">{{types[type]}}</option>
                    </select>
                </div>
                <div class="controls">
                    <label for="entry_tags">Tags</label>
                    <input id="entry_tags" class="longest" type="text" placeholder="Post Tags"/>
                </div>
            </div>
            <div class="control-group">
                <div class="controls">
                    <button id="post_btn" type="button" class="btn">Submit Post</button>
                </div>
            </div>
            <div class="control-group">
                <div class="controls">
                    <span id="post_output" class="alert hide alert-danger"></span>
                </div>
            </div>
        </form>
    </span>
    {% endblock %}
</div>
{% endblock %}