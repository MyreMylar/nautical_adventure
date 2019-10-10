import random
import math


class Wind:

    def __init__(self, min_wind, max_wind):
        self.min = min_wind
        self.max = max_wind
        self.min_change = -3
        self.max_change = 3
        self.time_accumulator = 0.0
        
        self.time_until_wind_changes = float(random.randint(5, 10))  # wind changes every five to ten seconds

        self.last_changes = [0, 0]
        self.wind_vector = [random.randint(self.min, self.max), random.randint(self.min, self.max)]
        self.current_value = int(math.sqrt(self.wind_vector[0] ** 2 + self.wind_vector[1] ** 2))
        self.direction = [self.wind_vector[0] / self.current_value, self.wind_vector[1] / self.current_value]
        self.calculate_new_wind_values()
        
    def update(self, time_delta):
        # the time_delta value is the amount of time in seconds since
        # the last loop of the game. We add it to the 'accumulator'
        # to track when an amount of time has passed, in this case
        # 5 to 10 seconds
        self.time_accumulator += time_delta
        if self.time_accumulator >= self.time_until_wind_changes:
            self.time_until_wind_changes = float(random.randint(5, 10))
            self.time_accumulator = 0.0  # reset the time accumulator
            self.calculate_new_wind_values()

    def calculate_new_wind_values(self):
        if self.last_changes[0] > 0:
            x_value = random.uniform(-1, self.max_change)
        elif self.last_changes[0] < 0:
            x_value = random.uniform(self.min_change, 1)
        else:
            x_value = random.randint(-1, 1)

        if self.last_changes[1] > 0:
            y_value = random.uniform(-1, self.max_change)
        elif self.last_changes[1] < 0:
            y_value = random.uniform(self.min_change, 1)
        else:
            y_value = random.randint(-1, 1)
        
        self.last_changes = [x_value, y_value]
        self.wind_vector = [self.wind_vector[0] + x_value, self.wind_vector[1] + y_value]
        if self.wind_vector[0] > self.max:
            self.wind_vector[0] = self.max
            self.last_changes[0] = -1
        if self.wind_vector[1] > self.max:
            self.wind_vector[1] = self.max
            self.last_changes[1] = -1
        if self.wind_vector[0] < self.min:
            self.wind_vector[0] = self.min
            self.last_changes[0] = 1
        if self.wind_vector[1] < self.min:
            self.wind_vector[1] = self.min
            self.last_changes[1] = 1
            
        self.current_value = int(math.sqrt(self.wind_vector[0] ** 2 + self.wind_vector[1] ** 2))
        self.direction = [self.wind_vector[0] / self.current_value, self.wind_vector[1] / self.current_value]
