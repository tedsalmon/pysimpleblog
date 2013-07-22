{% extends "base.tpl" %}
{% block body %}
<article class="blog-content">
    <header>
        <hgroup>
            <h2 class="muted">{{title}}</h2>
            <h5>by {{author}} on {{date.strftime('%B %d, %Y %H:%M')}}</h5>
            {% if user_login %}
            <div class="blog-post-control">
                <a title="Edit Post" class="icon-edit" href="/admin/post-editor/{{_id}}"></a>
                <a id="delete_post" title="Delete Post" class="icon-ban-circle" href="#" data-post-id="{{_id}}"></a>
            </div>
            {% endif %}
        </hgroup>
    </header>
    <div>{{body}}</div>
    <div class="blog-tags">Tagged {% for tag in tags %}{{'<a class="blog-tag muted" href="/tags/%s">%s</a> ' % (tag.strip(), tag)}}{% endfor %}</div>
    <h3>Add Comment</h3>
    <form>
        <div class="control-group">
            <div class="control-group">
                <div class="controls">
                    <input type="text" id="comment_name" placeholder="Name">
                </div>
            </div>
            <div class="control-group">
                <div class="controls">
                    <input type="text" id="comment_email" placeholder="Email">
                </div>
            </div>
            <div class="control-group">
                <div class="controls">
                    <textarea class="long-textarea" rows="5" id="comment_comment" placeholder="Comment"></textarea>
                </div>
            </div>
            <div class="control-group">
                <div class="controls">
                    <input id="comment_post_id" type="hidden" value="{{_id}}" />
                    <button id='comment_submit' type="button" class="btn">Submit</button>
                </div>
            </div>
            <div class="control-group">
                <div class="controls">
                    <div id="comment_output" class="size-quarter alert hide"></div>
                </div>
            </div>
        </div>
    </form>
    <h3>Comments</h3>
    <div id="comments" class="blog-comments">
    {% if comments %}
        {% for comment in comments %}
        <div class="blog-comment">
            <div>{{comment['name']}} wrote on {{comment['date'].strftime('%B %d, %Y %H:%M')}}:</div>
            <div class="blog-comment-body">{{comment['comment']}}</div>
        </div>
        {% endfor %}
    {% else %}
        <h5>No comments yet</h5>
    {% endif %}
    </div>
</article>
{% endblock %}