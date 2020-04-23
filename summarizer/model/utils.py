"""Provide utils for the summarizer."""
from operator import length_hint


class ItemsCount:
    """Count the items in the message."""

    def __init__(self, value):
        """Initialize the counter."""
        self._value = value
        self.string_types = (str)

    def __call__(self, sequence):
        """Return the count of items."""
        if isinstance(self._value, self.string_types):
            if self._value.endswith("%"):
                total_count = len(sequence)
                percentage = int(self._value[:-1])
                # at least one sentence should be chosen
                count = max(1, total_count * percentage // 100)
                return sequence[:count]
            return sequence[:int(self._value)]
        if isinstance(self._value, (int, float)):
            return sequence[:int(self._value)]
        return ValueError(f'Unsuported value of items count {self._value}.')

    def __repr__(self):
        """Return the printed version of item count."""
        return f"<ItemsCount: {self._value}>"


def maybe_get(cont, key, default=None):
    """Return the a value for the given key."""
    return cont[key] if key in cont else default


def get_msg_text(msg):
    """Pull the appropriate text from the message."""
    if 'text' in msg and msg['text']:
        return msg['text']
    if 'attachments' in msg:
        if msg['attachments']:
            attachment = msg['attachments'][0]
            att_text = []
            if 'title' in attachment:
                att_text.append(attachment['title'])
            if 'text' in attachment:
                att_text.append(attachment['text'])
            max_text = max(att_text, key=length_hint)
            if max_text:
                return max_text
    return ''
