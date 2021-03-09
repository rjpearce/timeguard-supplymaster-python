""" Implementation of a Timeguard Timeslot """

class TimeSlot:
    """ A single time entry when the device should be on or off """
    attributes = {}
    DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

    def __init__(self, attributes):
        self.attributes = attributes

    def translate_days_value(self, days):
        """ Translate days from int to human readable """
        translated_days = []
        for dow in days:
            translated_days.append(self.DAYS[int(dow)])
        if len(translated_days) == 0:
            return 'None'
        return ','.join(translated_days)

    # pylint: disable=too-many-arguments
    def set_time(self, days, start_time, end_time, start_enabled=True, end_enabled=True):
        """ Set the time configured for the time slot """
        for day in days:
            if day in self.DAYS:
                self.attributes['map'][str(int(self.DAYS.index(day)))] = str(
                    int(days[day]))
                self.attributes['end']['enable'] = str(int(end_enabled))
                self.attributes['end']['time'] = end_time
                self.attributes['start']['enable'] = str(int(start_enabled))
                self.attributes['start']['time'] = start_time
            else:
                print(f'Unknown day {day}')

    def reset(self):
        """ Reset the timeslot back to defaults """
        for day in self.DAYS:
            self.attributes['map'][str(self.DAYS.index(day))] = '0'
            self.attributes['end']['enable'] = '0'
            self.attributes['end']['time'] = '00:00'
            self.attributes['start']['enable'] = '0'
            self.attributes['start']['time'] = '00:00'

    def to_json(self):
        """ Render the timeslot in JSON format """
        return {
            "start": self.attributes['start'],
            "end": self.attributes['end'],
            "map": self.attributes['map']
        }

    def __repr__(self):
        days = self.translate_days_value(self.attributes['map'])
        start_time = self.attributes['start']['time']
        start_enabled = bool(int(self.attributes['start']['enable']))
        end_time = self.attributes['end']['time']
        end_enabled = bool(int(self.attributes['end']['enable']))
        return "\n%s(%s) to %s(%s) on %s" % (start_time, start_enabled, end_time, end_enabled, days)
