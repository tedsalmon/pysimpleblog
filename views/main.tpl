{% extends "base.tpl" %}
{% block body %}
<div class="blog-content divider-right span9">
    {% for post in posts %}
    {% set year = post['date'].strftime('%Y') %}
    <article>
        <header>
            <hgroup>
                <h2><a class="muted" href="/{{year}}/{{post['url']}}">{{post['title']}}</a></h2>
                <h5>by {{post['author']}} on {{post['date'].strftime('%m-%d-%Y %H:%M')}}</h5>
                {% if user_login %}
                <div class="blog-post-control">
                    <a title="Edit Post" class="icon-edit" href="/admin/post-editor/{{post['_id']}}"></a>
                    <a title="Delete Post" class="delete-post icon-ban-circle" href="#" data-post-id="{{post['_id']}}"></a>
                </div>
                {% endif %}
            </hgroup>
        </header>
        <div>{{post['body']}}</div>
        <div class="blog-tags">Tagged {% for tag in post['tags'] %}{{'<a class="link-underline muted" href="/tags/%s">%s</a> ' % (tag.strip().replace(' ','-'), tag)}}{% endfor %}</div>
        <div class="blog-comment-count">
            <b class="icon-comment"></b>
            <a class="muted" href="/{{year}}/{{post['url']}}#comments">{{post['comment_count']}} comments</a>
        </div>
    </article>
    {% endfor %}
    {% if posts|length == 10 %}
    <div class="blog-pagination" class="span11">
        <a class="muted" href='/page/{{page_id+1}}'>{{'\u2190'}} Older</a>
    </div>
    {% endif %}
</div>
<div class="blog-sidebar span3">
    <h3>Recent Posts</h3>
    <div>
        <ul class="blog-recent">
        {% for post in recent_posts%}
            <li><a class="muted" href="/{{year}}/{{post['url']}}">{{post['title']}}</a></li>
        {% endfor %}
        </ul>
    </div>
</div>
{% endblock %}