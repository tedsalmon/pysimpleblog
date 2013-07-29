{% extends "base.tpl" %}
{% block body %}
<article class="blog-content blog-page">
    <header>
        <hgroup>
            <h2>{{page['title']}}</h2>
            {% if user_id %}
            <div class="blog-post-control">
                <a title="Edit Post" class="icon-edit" href="/admin/post-editor/{{page['_id']}}"></a>
                <a id="delete_post" title="Delete Post" class="icon-ban-circle" href="#" data-post-id="{{page['_id']}}"></a>
            </div>
            {% endif %}
        </hgroup>
    </header>
    <div>{{page['body']}}</div>
</article>
{% endblock %}