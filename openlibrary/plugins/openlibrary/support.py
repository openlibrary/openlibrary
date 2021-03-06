import datetime

import web

from infogami import config
from infogami.utils import delegate
from infogami.utils.view import render_template
from infogami.utils.context import context

from openlibrary.core import support as S

support_db = None

class contact(delegate.page):
    def GET(self):
        i = web.input(path=None)
        email = context.user and context.user.email
        return render_template("support", email=email, url=i.path)

    def POST(self):
        if "support" in web.ctx.features:
            return self.POST_new()
        else:
            return self.POST_old()

    def POST_old(self):
        i = web.input(email='', url='', question='')
        fields = web.storage({
            'email': i.email,
            'irl': i.url,
            'comment': i.question,
            'sent': datetime.datetime.utcnow(),
            'browser': web.ctx.env.get('HTTP_USER_AGENT', '')
        })
        msg = render_template('email/spam_report', fields)
        web.sendmail(i.email, config.report_spam_address, msg.subject, str(msg))
        print config.report_spam_address
        return render_template("support", done = True)

    def POST_new(self):
        form = web.input()
        email = form.get("email", "")
        topic = form.get("topic", "")
        description = form.get("question", "")
        url = form.get("url", "")
        user = web.ctx.site.get_user()
        useragent = web.ctx.env.get("HTTP_USER_AGENT","")
        support_db.create_case(creator_name      = user and user.get_name() or "",
                               creator_email     = email,
                               creator_useragent = useragent,
                               subject           = topic,
                               description       = description,
                               url               = url,
                               assignee          = "mary@archive.org") # TBD. This has to be dynamic
        return render_template("support", done = True)


def setup():
    global support_db
    support_db = S.Support()

