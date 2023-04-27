from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.core.window import Window
from kivy.properties import ObjectProperty


class CircleDrawer(Widget):
    circle = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(CircleDrawer, self).__init__(**kwargs)
        self.focus = True  # Set focus to the widget to capture keyboard events
        with self.canvas:
            # Set the circle color
            Color(1, 0, 0)
            # Draw a tiny circle initially at the center of the window
            self.circle = Ellipse(pos=(Window.width // 2 - 5, Window.height // 2 - 5), size=(10, 10))
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        x, y = self.circle.pos
        step = 5

        if keycode[1] == 'up':
            y += step
        elif keycode[1] == 'down':
            y -= step
        elif keycode[1] == 'left':
            x -= step
        elif keycode[1] == 'right':
            x += step

        self.circle.pos = (x, y)
        return True


class CircleDrawerApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)  # Set the background color to white
        return CircleDrawer()


if __name__ == '__main__':
    CircleDrawerApp().run()