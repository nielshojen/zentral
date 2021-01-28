import json
from django.urls import reverse
from django.test import TestCase
from django.utils.crypto import get_random_string
import yaml
from accounts.forms import ServiceAccountForm
from zentral.contrib.inventory.models import Certificate, File
from zentral.contrib.santa.models import Configuration, Rule, RuleSet, Target


class APIViewsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.configuration = Configuration.objects.create(name=get_random_string(256))
        cls.configuration2 = Configuration.objects.create(name=get_random_string(256))
        service_account_form = ServiceAccountForm({"name": get_random_string()})
        assert(service_account_form.is_valid())
        cls.service_account = service_account_form.save()
        cls.maxDiff = None

    def post_data(self, url, data, content_type, include_token=True):
        kwargs = {"content_type": content_type}
        if include_token:
            kwargs["HTTP_AUTHORIZATION"] = f"Token {self.service_account.auth_token.key}"
        return self.client.post(url, data, **kwargs)

    def post_yaml_data(self, url, data, include_token=True):
        content_type = "application/yaml"
        data = yaml.dump(data)
        return self.post_data(url, data, content_type, include_token)

    def post_json_data(self, url, data, include_token=True):
        content_type = "application/json"
        data = json.dumps(data)
        return self.post_data(url, data, content_type, include_token)

    def test_ingest_fileinfo_unauthorized(self):
        url = reverse("santa_api:ingest_file_info")
        response = self.post_json_data(url, [], include_token=False)
        self.assertEqual(response.status_code, 401)

    def test_ruleset_update_unauthorized(self):
        url = reverse("santa_api:ruleset_update")
        response = self.post_json_data(url, {}, include_token=False)
        self.assertEqual(response.status_code, 401)

    def test_ingest_fileinfo(self):
        url = reverse("santa_api:ingest_file_info")
        data = [
            {'Bundle Name': '1Password 7',
             'Bundle Version': '70700015',
             'Bundle Version Str': '7.7',
             'Code-signed': 'Yes',
             'Path': '/Applications/1Password 7.app/Contents/MacOS/1Password 7',
             'Rule': 'Allowed (Unknown)',
             'SHA-1': '98f07121d283e305812798d42bd29da8ece10abe',
             'SHA-256': 'df469b87ae9221e5df3f0e585f05926865cef907d332934dc33a3fa4b6b2cc3a',
             'Signing Chain': [
                 {'Common Name': 'Developer ID Application: AgileBits Inc. (2BUA8C4S2C)',
                  'Organization': 'AgileBits Inc.',
                  'Organizational Unit': '2BUA8C4S2C',
                  'SHA-1': '2d0637d09a7ae4cf11668971b11ce56bfb56c5bc',
                  'SHA-256': '137868ff9b2caf3f640e71c847cd7fb870de6620c2dcc3a90287cf5a4a511940',
                  'Valid From': '2017/02/19 00:39:36 +0100',
                  'Valid Until': '2022/02/20 00:39:36 +0100'},
                 {'Common Name': 'Developer ID Certification Authority',
                  'Organization': 'Apple Inc.',
                  'Organizational Unit': 'Apple Certification Authority',
                  'SHA-1': '3b166c3b7dc4b751c9fe2afab9135641e388e186',
                  'SHA-256': '7afc9d01a62f03a2de9637936d4afe68090d2de18d03f29c88cfb0b1ba63587f',
                  'Valid From': '2012/02/01 23:12:15 +0100',
                  'Valid Until': '2027/02/01 23:12:15 +0100'},
                 {'Common Name': 'Apple Root CA',
                  'Organization': 'Apple Inc.',
                  'Organizational Unit': 'Apple Certification Authority',
                  'SHA-1': '611e5b662c593a08ff58d14ae22452d198df6c60',
                  'SHA-256': 'b0b1730ecbc7ff4505142c49f1295e6eda6bcaed7e2c68c5be91b5a11001f024',
                  'Valid From': '2006/04/25 23:40:36 +0200',
                  'Valid Until': '2035/02/09 22:40:36 +0100'}],
             'Type': 'Executable (x86_64)'},
            {'Type': 'YOLO'},
        ]
        file_qs = File.objects.filter(sha_256=data[0]['SHA-256'])
        cert_qs = Certificate.objects.filter(sha_256=data[0]['Signing Chain'][0]['SHA-256'])
        self.assertEqual(file_qs.count(), 0)
        self.assertEqual(cert_qs.count(), 0)
        response = self.post_json_data(url, data)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(
            json_response,
            {'added': 1,
             'db_errors': 0,
             'deserialization_errors': 0,
             'ignored': 1,
             'present': 0}
        )
        response = self.post_json_data(url, data)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(
            json_response,
            {'added': 0,
             'db_errors': 0,
             'deserialization_errors': 0,
             'ignored': 1,
             'present': 1}
        )
        self.assertEqual(file_qs.count(), 1)
        self.assertEqual(cert_qs.count(), 1)

    def test_ruleset_update_rule(self):
        url = reverse("santa_api:ruleset_update")

        # JSON rule for all configurations
        data = {
            "name": get_random_string(),
            "rules": [
                {"rule_type": "BINARY",
                 "sha256": get_random_string(64, "0123456789abcdef"),
                 "policy": "BLOCKLIST"}
            ]
        }
        self.assertEqual(self.configuration.rule_set.count(), 0)
        self.assertEqual(self.configuration2.rule_set.count(), 0)
        response = self.post_json_data(url, data)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        ruleset = RuleSet.objects.get(name=data["name"])
        self.assertEqual(
            json_response,
            {'ruleset': {
                'name': ruleset.name,
                'pk': ruleset.pk,
                'result': 'created'},
             'configurations': [
                {'name': self.configuration.name,
                 'pk': self.configuration.pk,
                 'rule_results': {'created': 1,
                                  'deleted': 0,
                                  'present': 0,
                                  'updated': 0}},
                {'name': self.configuration2.name,
                 'pk': self.configuration2.pk,
                 'rule_results': {'created': 1,
                                  'deleted': 0,
                                  'present': 0,
                                  'updated': 0}}]}
        )
        self.assertEqual(self.configuration.rule_set.count(), 1)
        self.assertEqual(self.configuration2.rule_set.count(), 1)
        self.assertEqual(
            self.configuration.rule_set.filter(
                target__type=Target.BINARY,
                target__sha256=data["rules"][0]["sha256"],
                policy=Rule.BLOCKLIST,
                custom_msg="",
                ruleset=ruleset,
            ).count(), 1
        )
        self.assertEqual(
            self.configuration2.rule_set.filter(
                target__type=Target.BINARY,
                target__sha256=data["rules"][0]["sha256"],
                policy=Rule.BLOCKLIST,
                custom_msg="",
                ruleset=ruleset,
            ).count(), 1
        )
        self.assertEqual(self.configuration2.rule_set.count(), 1)

        # idempotent / YAML
        response = self.post_yaml_data(url, data)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(
            json_response,
            {'ruleset': {
                'name': ruleset.name,
                'pk': ruleset.pk,
                'result': 'present'},
             'configurations': [
                {'name': self.configuration.name,
                 'pk': self.configuration.pk,
                 'rule_results': {'created': 0,
                                  'deleted': 0,
                                  'present': 1,
                                  'updated': 0}},
                {'name': self.configuration2.name,
                 'pk': self.configuration2.pk,
                 'rule_results': {'created': 0,
                                  'deleted': 0,
                                  'present': 1,
                                  'updated': 0}}]}
        )
        self.assertEqual(self.configuration.rule_set.count(), 1)
        self.assertEqual(self.configuration2.rule_set.count(), 1)

        # update
        data["rules"][0]["custom_msg"] = get_random_string()
        response = self.post_json_data(url, data)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        ruleset = RuleSet.objects.get(name=data["name"])
        self.assertEqual(
            json_response,
            {'ruleset': {
                'name': ruleset.name,
                'pk': ruleset.pk,
                'result': 'present'},
             'configurations': [
                {'name': self.configuration.name,
                 'pk': self.configuration.pk,
                 'rule_results': {'created': 0,
                                  'deleted': 0,
                                  'present': 0,
                                  'updated': 1}},
                {'name': self.configuration2.name,
                 'pk': self.configuration2.pk,
                 'rule_results': {'created': 0,
                                  'deleted': 0,
                                  'present': 0,
                                  'updated': 1}}]}
        )
        self.assertEqual(self.configuration.rule_set.count(), 1)
        self.assertEqual(self.configuration2.rule_set.count(), 1)
        self.assertEqual(
            self.configuration.rule_set.filter(
                target__type=Target.BINARY,
                target__sha256=data["rules"][0]["sha256"],
                policy=Rule.BLOCKLIST,
                custom_msg=data["rules"][0]["custom_msg"],
                ruleset=ruleset,
            ).count(), 1
        )
        self.assertEqual(
            self.configuration2.rule_set.filter(
                target__type=Target.BINARY,
                target__sha256=data["rules"][0]["sha256"],
                policy=Rule.BLOCKLIST,
                custom_msg=data["rules"][0]["custom_msg"],
                ruleset=ruleset,
            ).count(), 1
        )

        # scoped + conflict
        data2 = {
            "name": get_random_string(),
            "configurations": [self.configuration.name],
            "rules": [
                {"rule_type": "BINARY",
                 "sha256": data["rules"][0]["sha256"],
                 "policy": "ALLOWLIST"}
            ]
        }
        response = self.post_json_data(url, data2)
        self.assertEqual(response.status_code, 400)
        json_response = response.json()
        self.assertEqual(
            json_response,
            {"rules": {"0": {"non_field_errors": ["conflict"]}}}
        )
        self.assertEqual(self.configuration.rule_set.count(), 1)
        self.assertEqual(self.configuration2.rule_set.count(), 1)
        self.assertEqual(RuleSet.objects.filter(name=data2["name"]).count(), 0)

        # new scoped ruleset
        data2["rules"][0]["sha256"] = get_random_string(64, "0123456789abcdef")
        response = self.post_json_data(url, data2)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        ruleset2 = RuleSet.objects.get(name=data2["name"])
        self.assertEqual(
            json_response,
            {'ruleset': {
                'name': ruleset2.name,
                'pk': ruleset2.pk,
                'result': 'created'},
             'configurations': [
                {'name': self.configuration.name,
                 'pk': self.configuration.pk,
                 'rule_results': {'created': 1,
                                  'deleted': 0,
                                  'present': 0,
                                  'updated': 0}}]}
        )
        self.assertEqual(self.configuration.rule_set.count(), 2)
        self.assertEqual(self.configuration2.rule_set.count(), 1)
        self.assertEqual(
            self.configuration.rule_set.filter(
                target__type=Target.BINARY,
                target__sha256=data2["rules"][0]["sha256"],
                policy=Rule.ALLOWLIST,
                ruleset=ruleset2,
            ).count(), 1
        )

        # delete last rule / YAML
        data2["rules"] = []
        response = self.post_json_data(url, data2)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(
            json_response,
            {'ruleset': {
                'name': ruleset2.name,
                'pk': ruleset2.pk,
                'result': 'present'},
             'configurations': [
                {'name': self.configuration.name,
                 'pk': self.configuration.pk,
                 'rule_results': {'created': 0,
                                  'deleted': 1,
                                  'present': 0,
                                  'updated': 0}}]}
        )
        self.assertEqual(self.configuration.rule_set.count(), 1)
        self.assertEqual(self.configuration2.rule_set.count(), 1)
