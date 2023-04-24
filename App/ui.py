import pygame_gui
import pygame
def draw_boundary_limits(screen, x_min, x_max, y_min, y_max, color=(0, 255, 0)):
    pygame.draw.line(screen, color, (x_min, y_min), (x_min, y_max), 2)  # Left vertical line
    pygame.draw.line(screen, color, (x_max, y_min), (x_max, y_max), 2)  # Right vertical line
    pygame.draw.line(screen, color, (x_min, y_min), (x_max, y_min), 2)  # Top horizontal line
    pygame.draw.line(screen, color, (x_min, y_max), (x_max, y_max), 2)  # Bottom horizontal line

def handle_slider_events(event, ui_elements):
    if hasattr(event, 'user_type'):
        if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == ui_elements.kp_slider:
                ui_elements.agent.kp = event.value
                ui_elements.kp_label.set_text(f"KP: {ui_elements.agent.kp:.2f}")
            elif event.ui_element == ui_elements.kd_slider:
                ui_elements.agent.kd = event.value
                ui_elements.kd_label.set_text(f"KD: {ui_elements.agent.kd:.2f}")
            elif event.ui_element == ui_elements.steering_scalar_slider:
                ui_elements.agent.steering_scalar = event.value
                ui_elements.steering_scalar_label.set_text(f"Steering Scalar: {ui_elements.agent.steering_scalar:.2f}")

class UIElements:
    def __init__(self, manager, agent):
        self.agent = agent
        self.kp_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((10, 10), (200, 20)),
            start_value=1.5,
            value_range=(0.0, 5.0),
            manager=manager,
        )

        self.kd_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((10, 40), (200, 20)),
            start_value=2.0,
            value_range=(0.0, 5.0),
            manager=manager,
        )

        self.steering_scalar_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((10, 70), (200, 20)),
            start_value=0.5,
            value_range=(0.0, 2.0),
            manager=manager,
        )

        self.kp_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((220, 10), (100, 20)),
            text="KP: 1.5",
            manager=manager,
        )

        self.kd_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((220, 40), (100, 20)),
            text="KD: 2.0",
            manager=manager,
        )

        self.steering_scalar_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((220, 70), (150, 20)),
            text="Steering: 0.5",
            manager=manager,
        )

    def update(self):
        self.kp_label.set_text(f"KP: {self.agent.kp:.2f}")
        self.kd_label.set_text(f"KD: {self.agent.kd:.2f}")
        self.steering_scalar_label.set_text(f"Steering: {self.agent.steering_scalar:.2f}")
