from app.extensions import sitemapper


sitemapper.add_endpoint("main.index", priority=1.0)
sitemapper.add_endpoint("docs.index")
sitemapper.add_endpoint("docs.get_started")
sitemapper.add_endpoint("docs.concepts")
sitemapper.add_endpoint("docs.tutorials")
sitemapper.add_endpoint("main.privacy_policy")
sitemapper.add_endpoint("main.terms_of_service")
sitemapper.add_endpoint("main.faq")
