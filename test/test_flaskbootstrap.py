from test_views import TestViews
try:
    from flask_bootstrap import Bootstrap, bootstrap_find_resource
except ImportError:
    pass


class TestFlaskBootstrap(TestViews):
    """
    this is the only condition where flask_bootstrap
    will be used in the templates
    """

    def other_config(self):
        Bootstrap(self.app)
        self.app.config["BLOGGING_FLASK_BOOTSTRAP"] = True

    def test_bootstrap_find_resource(self):
        """
        validating that the engine has set the cdn for flask_bootstrap
        and that bootstrap_find_resource creates a url.
        """
        with self.app.app_context():
            mathjax = bootstrap_find_resource('test',
                                              cdn='mathjax',
                                              use_minified=False)
            self.assertEqual(mathjax, '//cdn.mathjax.org/mathjax/latest/test')


class TestBootstrapDisabled(TestViews):
    """
    flask_bootstrap is available but not used
    """

    def other_config(self):
        Bootstrap(self.app)
        self.app.config["BLOGGING_FLASK_BOOTSTRAP"] = False


class TestNoBootstrap(TestViews):
    """
    flask_bootstrap not avalible
    this will create exception
    """

    def other_config(self):
        self.app.config["BLOGGING_FLASK_BOOTSTRAP"] = True

    def _create_blogging_engine(self):
        try:
            super(TestNoBootstrap, self)._create_blogging_engine()
        except Exception as e:
            print(e.message)
            self.assertEqual('Flask_Bootstrap extention not found.',
                             str(e.message))
        self.skipTest(TestNoBootstrap)
