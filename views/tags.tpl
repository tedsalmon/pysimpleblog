{% extends "base.tpl" %}
{% block body %}
<div class="blog-content">
    {% if not posts %}
    <h2>No posts tagged as "{{tag | e}}"</h2>
    {% else %}
    <h2>Posts tagged as {{tag | e}}:</h2>
    {% for post in posts %}
    <article>
        <header>
            <hgroup>
                <h2><a class="muted" href="/{{post['_id']}}/{{post['url_name']}}">{{post['title']}}</a></h2>
                <h5>by {{post['author']}} on {{post['date'].strftime('%m-%d-%Y %H:%M')}}</h5>
                {% if user_login %}
                <div class="blog-post-control">
                    <a title="Edit Post" class="icon-edit" href="/admin/post-editor/{{post['url_id']}}"></a>
                    <a id="delete_post" title="Delete Post" class="icon-ban-circle" href="#" data-post-id="{{url_id}}"></a>
                </div>
                {% endif %}
            </hgroup>
        </header>
        <div>{{post['body']}}</div>
        <div class="blog-tags">Tagged {% for tag in post['tags'] %}{{'<a class="blog-tag muted" href="/tags/%s">%s</a> ' % (tag.strip(), tag)}}{% endfor %}</div>
        <div class="blog-comment-count">
            <b class="icon-comment"></b>
            <a class="muted" href="/{{post['_id']}}/{{post['url_name']}}#comments">{{post['comment_count']}} comments</a>
        </div>
    </article>
    {% endfor %}
    {% endif %}
</div>
{% endblock %}