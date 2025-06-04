import unittest
from unittest.mock import patch, Mock
from django.test import TestCase, override_settings
from tickets.models import Ticket
from tickets.telegram_utils import send_new_ticket_notification
from django.utils import timezone


@override_settings(TELEGRAM_BOT_TOKEN='token', TELEGRAM_CHAT_ID='123')
class SendNewTicketNotificationTests(TestCase):
    def _create_ticket(self):
        return Ticket.objects.create(
            full_name='Test User',
            phone='12345',
            internal_phone='6789',
            building='A',
            office='101',
            error_description='desc',
            email='test@example.com',
            created_at=timezone.now()
        )

    @patch('tickets.telegram_utils.requests.post')
    def test_success(self, mock_post):
        mock_resp = Mock(status_code=200, text='OK')
        mock_post.return_value = mock_resp
        ticket = self._create_ticket()
        success, error = send_new_ticket_notification(ticket)
        self.assertTrue(success)
        self.assertIsNone(error)
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn('chat_id', kwargs['data'])
        self.assertEqual(kwargs['data']['chat_id'], '123')

    @patch('tickets.telegram_utils.requests.post')
    def test_migrate_chat_id(self, mock_post):
        first = Mock(status_code=400)
        first.json.return_value = {'parameters': {'migrate_to_chat_id': '999'}}
        second = Mock(status_code=200)
        mock_post.side_effect = [first, second]
        ticket = self._create_ticket()
        success, error = send_new_ticket_notification(ticket)
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertEqual(mock_post.call_count, 2)
        first_call = mock_post.call_args_list[0]
        second_call = mock_post.call_args_list[1]
        self.assertEqual(first_call.kwargs['data']['chat_id'], '123')
        self.assertEqual(second_call.kwargs['data']['chat_id'], '999')

    @patch('tickets.telegram_utils.requests.post')
    def test_network_error(self, mock_post):
        mock_post.side_effect = Exception('boom')
        ticket = self._create_ticket()
        success, error = send_new_ticket_notification(ticket)
        self.assertFalse(success)
        self.assertIn('Сетевая ошибка', error)

    @patch('tickets.telegram_utils.requests.post')
    def test_api_error(self, mock_post):
        resp = Mock(status_code=500, text='oops')
        resp.json.side_effect = ValueError
        mock_post.return_value = resp
        ticket = self._create_ticket()
        success, error = send_new_ticket_notification(ticket)
        self.assertFalse(success)
        self.assertEqual(error, 'Telegram API 500: oops')
