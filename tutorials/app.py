# %%
from fasthtml.common import *

# app = FastHTML()
app = FastHTMLWithLiveReload()
@app.get("/")
def home():
    page = Html(
        Head(Title('nice head')),
        Body(Div('Some text I will write here more, ', A('A link', href='https://example.com'), Img(src="https://placehold.co/200"), cls='myclass')))
    return page

serve()
