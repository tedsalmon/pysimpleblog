<!DOCTYPE html>
<html lang="en">
    <head>
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta http-equiv="content-type" content='text/html; charset=utf-8' charset='UTF-8' />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta name="description" content="{{site_description}}" />
        <meta name="keywords" content="{{site_keywords}}" />
        <title>{% if sub_title %}{{sub_title}} | {%endif%}{{site_title}}</title>
        <link href="//cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/2.3.2/css/bootstrap.min.css" rel="stylesheet" />
        <link href="//cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/2.3.2/css/bootstrap-responsive.min.css" rel="stylesheet" />
        <link href="//cdnjs.cloudflare.com/ajax/libs/x-editable/1.4.5/bootstrap-editable/css/bootstrap-editable.css" rel="stylesheet"/>
        <link href="/static/css/style.css" rel="stylesheet" />
        <link rel="icon" href="/static/favicon.ico" type="image/x-ico" />
    </head>
    <body>
        <div class="blog-main container">
            <header class="blog-banner">
                <hgroup>
                    <h2 class="blog-brand"><a class="muted blog-brand-link" href="/">{{site_header}}</a></h2>
                    <h5 class="muted">{{site_subheader}}</h5>
                </hgroup>
            </header>
            <div class="navbar">
                <div class="blog-nav navbar-inner">
                    <div class="container">
                        <button type="button" class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
                            <span class="icon-bar"></span>
                            <span class="icon-bar"></span>
                            <span class="icon-bar"></span>
                        </button>
                        <nav class="nav-collapse collapse">
                            <ul class="nav">
                                <li><a href="/">Home</a></li>
                                <li><a href="/archive">Archives</a></li>
                                {% if nav_links %}
                                {%for link in nav_links %}
                                <li><a href="{{link['url']}}">{{link['title']}}</a></li>
                                {%endfor%}
                                {% endif %}
                                {%if user_id %}
                                <li class="divider-vertical"></li>
                                <li class="dropdown">
                                    <a href="/admin" class="dropdown-toggle" data-toggle="dropdown">Admin<b class="caret"></b></a>
                                    <ul class="dropdown-menu">
                                        {% include 'admin/admin_links.tpl' %}
                                    </ul>
                                </li>
                                {% endif %}
                            </ul>
                            <div class="blog-nav-extras pull-right">
                                <form class="navbar-search" action="http://google.com/search" method="GET">
                                    <input type="hidden" name="q" value="site:{{site_url}}">
                                    <input type="text" class="search-query" name="q" results="0" placeholder="Search">
                                </form>
                            {% if user_id %}
                                <span class="dropdown blog-user">
                                    <span class="icon-user"></span>
                                    <a class="dropdown-toggle muted clickable" data-toggle="dropdown">Hello, {{user_id}} <b class="muted-border caret"></b></a>
                                    <ul class="dropdown-menu" role="menu" aria-labelledby="dLabel">
                                        <li><a href="/admin/view-profile">My Profile</a></li>
                                        <li><a class="blog-logout clickable">Logout</a></li>
                                    </ul>
                                </span>
                            {% else %}
                                <span class="blog-user">
                                    <span class="icon-user"></span>
                                    <a id="login_modal_btn" class="muted clickable">Login</a>
                                </span>
                            {% endif %}
                            </div>
                        </nav>
                    </div>
                </div>
            </div>
            <div class="blog-container container-fluid">
                <div class="row-fluid">
                    {% block body %}
                    {% endblock %}
                </div>
            </div>
            <footer class="blog-footer">{{site_footer}}</footer>
        <!-- Modals -->
        <div id="login_modal" class="modal hide fade">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                <h3>Login</h3>
                <h5 id="login_output" class="alert alert-danger text-center hide"></h5>
            </div>
            <div class="modal-body">
                <form class="form-horizontal">
                    <div class="control-group">
                        <div class="controls">
                            <input type="text" id="login_username" placeholder="Username" />
                        </div>
                    </div>
                    <div class="control-group">
                        <div class="controls">
                            <input type="password" id="login_password" placeholder="Password" />
                        </div>
                    </div>
                    <div class="control-group">
                        <div class="controls">
                            <input class="no-margin" type="checkbox" id="login_remember" />
                            <label class="blog-login-remember" for="login_remember">Remember Me</label>
                        </div>
                    </div>
                    <div class="control-group">
                        <div class="controls">
                            <button id="login_btn" type="button" class="btn">Login</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
        {% if user_id %}
        <div id="delete_modal" class="modal hide fade">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                <h3>Are you sure you want to delete this post?</h3>
            </div>
            <div class="modal-body">
                <form class="form text-center" action="#">
                    <div class="control-group">
                        <div class="controls">
                            <a id="delete_confirm" class="btn clickable" data-dismiss="modal">Yes</a>
                            <a class="left-space btn clickable" data-dismiss="modal">No</a>
                        </div>
                    </div>
                </form>
            </div>
        </div>
        {% endif %}
        <!-- Scripts -->
        <script type='text/javascript' src='//cdnjs.cloudflare.com/ajax/libs/jquery/2.0.3/jquery.min.js'></script>
        <script type='text/javascript' src='//cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/2.3.2/js/bootstrap.min.js'></script>
        <script src="//cdnjs.cloudflare.com/ajax/libs/x-editable/1.4.5/bootstrap-editable/js/bootstrap-editable.min.js"></script>
        <script type="text/javascript" src="/static/js/main.js"></script>
        {% if site_ga_key and site_url %}
        <script type="text/javascript">
            var _gaq = _gaq || [];
            _gaq.push(['_setAccount', '{{site_ga_key}}']);
            _gaq.push(['_trackPageview']);
            (function() {
              var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
              ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
              var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
            })();
        </script>
        {% endif %}
        {% if user_id %}<script type="text/javascript" src="/static/js/admin.js"></script>{% endif %}
        <script>
            (function(){
                Blog.init();
                if(Blog.Admin)
                    Blog.Admin.init();
            })();
        </script>
    </body>
</html>