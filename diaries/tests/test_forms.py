from django.test import SimpleTestCase

from ..forms import DiaryForm


class DiaryFormTest(SimpleTestCase):
    def test_form_with_no_data_isnt_valid(self):
        data = {}
        form = DiaryForm(data=data)
        self.assertFalse(form.is_valid())

    def test_form_with_empty_data_isnt_valid(self):
        data = {
            'title': '',
            'content': ''
        }
        form = DiaryForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form['title'].errors)
        self.assertTrue(form['content'].errors)

    def test_form_with_minimum_data_is_valid(self):
        data = {
            'title': 'A test diary',
            'content': 'Some content'
        }
        form = DiaryForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_content_with_malicious_data(self):
        malicious_html = 'Some <p>content</p><script>alert("Hello");</script>'
        escaped_html = 'Some <p>content</p>&lt;script&gt;alert("Hello");&lt;/script&gt;'
        data = {
            'title': 'A test diary',
            'content': malicious_html
        }
        form = DiaryForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['content'], escaped_html)
