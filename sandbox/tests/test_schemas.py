"""Schema 定义和接口测试"""
from django.test import TestCase

from sandbox.schemas import SANDBOX_TYPE_SCHEMAS, get_type_schema, get_all_type_schemas


class TestSandboxTypeSchemas(TestCase):
    def test_all_four_types_exist(self):
        """四种沙箱类型都存在"""
        self.assertEqual(
            set(SANDBOX_TYPE_SCHEMAS.keys()),
            {"localdocker", "remotedocker", "localsystem", "remotesystem"},
        )

    def test_localdocker_schema(self):
        """localdocker 包含 image 和 work_dir，不含 root_path 和 ssh_host"""
        schema = get_type_schema("localdocker")
        self.assertIn("image", schema["fields"])
        self.assertIn("work_dir", schema["fields"])
        self.assertNotIn("root_path", schema["fields"])
        self.assertNotIn("ssh_host", schema["fields"])

    def test_localsystem_schema(self):
        """localsystem 包含 root_path 和 work_dir"""
        schema = get_type_schema("localsystem")
        self.assertIn("root_path", schema["fields"])
        self.assertIn("work_dir", schema["fields"])
        self.assertEqual(schema["fields"]["root_path"]["default"], "sandbox/")
        self.assertEqual(schema["fields"]["work_dir"]["default"], "workspace")

    def test_remotesystem_schema(self):
        """remotesystem 包含 root_path、work_dir 和 SSH 字段"""
        schema = get_type_schema("remotesystem")
        self.assertIn("root_path", schema["fields"])
        self.assertIn("work_dir", schema["fields"])
        self.assertIn("ssh_host", schema["fields"])
        self.assertIn("ssh_port", schema["fields"])
        self.assertIn("ssh_user", schema["fields"])
        self.assertIn("ssh_key_path", schema["fields"])
        self.assertIn("ssh_password", schema["fields"])

    def test_remotedocker_schema(self):
        """remotedocker 包含 image、work_dir 和 SSH 字段，不含 root_path"""
        schema = get_type_schema("remotedocker")
        self.assertIn("image", schema["fields"])
        self.assertIn("work_dir", schema["fields"])
        self.assertIn("ssh_host", schema["fields"])
        self.assertNotIn("root_path", schema["fields"])

    def test_field_metadata_structure(self):
        """每个字段都有 type、required、default、label、hint"""
        for type_name in SANDBOX_TYPE_SCHEMAS:
            schema = get_type_schema(type_name)
            for field_name, field_meta in schema["fields"].items():
                self.assertIn("type", field_meta, f"{type_name}.{field_name} 缺少 type")
                self.assertIn("required", field_meta, f"{type_name}.{field_name} 缺少 required")
                self.assertIn("label", field_meta, f"{type_name}.{field_name} 缺少 label")

    def test_get_all_type_schemas(self):
        """get_all_type_schemas 返回包含 types 键的字典，内含 4 种类型"""
        result = get_all_type_schemas()
        self.assertIn("types", result)
        self.assertEqual(len(result["types"]), 4)

    def test_unknown_type_raises(self):
        """未知类型抛出 ValueError"""
        with self.assertRaises(ValueError):
            get_type_schema("unknown_type")
