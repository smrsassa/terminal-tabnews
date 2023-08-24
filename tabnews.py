from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Footer, Header, Static, TabbedContent, TabPane, Markdown, Button
from textual.screen import Screen
from textual.reactive import reactive

import requests


API = "https://www.tabnews.com.br/api/v1/"

POST_INFO = {
    "user": "",
    "url": ""
}

class Text(Static):
    """ Só para dar display em uma string """

class PostViewer(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Fechar post")]

    postData = reactive(dict())

    def watch_postData(self):
        if self.postData != dict():
            new_md = Markdown("# "+ self.postData['title'] +"\n"+ self.postData['body'])
            self.mount(new_md)

    def _on_screen_suspend(self) -> None:
        mds = self.query("Markdown")
        if mds:
            mds.last().remove()

        return super()._on_screen_suspend()

    def _on_screen_resume(self) -> None:
        response = requests.get(API +"contents/"+ POST_INFO['user'] + "/"+ POST_INFO['url'])

        if response.status_code == 200:
            self.postData = response.json()

        return super()._on_screen_resume()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

class PostLink(Static):
    def __init__(self, user, url, title, created_at, tabcoins, comentarios) -> None:
        self.user = user
        self.url = url
        self.title = title
        self.created_at = created_at
        self.tabcoins = tabcoins
        self.comentarios = comentarios

        super().__init__()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global POST_INFO
        POST_INFO = {
            "user": self.user,
            "url": self.url
        }

        self.app.push_screen("screen_post_viewer")

    def compose(self) -> ComposeResult:
        postPrefix = str(self.tabcoins) +" tabcoins · "+ str(self.comentarios) +" comentário · "+ str(self.user)
        yield Button(postPrefix.ljust(50) +" | "+ self.title)

class Content(Static):
    def __init__(self, estrategia = "relevant") -> None:
        self.estrategia = estrategia

        super().__init__()

    def compose(self) -> ComposeResult:
        response = requests.get(API +"contents?strategy="+ self.estrategia)

        if response.status_code == 200:
            data = response.json()

            for post in data:
                yield PostLink(post['owner_username'], post['slug'], post['title'], post['created_at'], post['tabcoins'], post['children_deep_count'])
        else:
            yield Text("Erro ao conectar com a API do TabNews! Verifique sua conexão com a internet\nStatus Code: "+ str(response.status_code))


class ContentList(Screen):
    BINDINGS = [
        ("r", "show_tab('tab_relevantes')", "Relevantes"),
        ("n", "show_tab('tab_recentes')", "Recente")
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with TabbedContent(initial="tab_relevantes"):
            with TabPane("Relevantes", id="tab_relevantes"):
                yield ScrollableContainer(Content())
            with TabPane("Recentes", id="tab_recentes"):
                yield ScrollableContainer(Content("new"))

    def action_show_tab(self, tab: str) -> None:
        self.get_child_by_type(TabbedContent).active = tab

class TabNews(App):
    CSS_PATH = "tabnews.css"

    def on_mount(self) -> None:
        self.install_screen(ContentList(), name="screen_content_list")
        self.install_screen(PostViewer(), name="screen_post_viewer")

        self.app.push_screen("screen_content_list")

if __name__ == "__main__":
    app = TabNews()
    app.run()
