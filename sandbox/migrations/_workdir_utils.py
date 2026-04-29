"""沙箱数据迁移工具：将 metadata 中的绝对路径转为相对路径"""


def migrate_absolute_to_relative(ElSandboxInstance):
    """将 ElSandboxInstance metadata 中的绝对路径转为相对路径

    设计原则：不向后兼容，有问题就报错。
    迁移失败时整个迁移回滚，不静默跳过。
    """
    for instance in ElSandboxInstance.objects.all():
        metadata = instance.metadata.copy()
        changed = False

        # work_dir: 去掉前导 /
        work_dir = metadata.get("work_dir", "")
        if work_dir.startswith("/"):
            metadata["work_dir"] = work_dir.lstrip("/")
            changed = True

        # root_path: 仅 System 类型，去掉前导 /
        if instance.type in ("localsystem", "remotesystem"):
            root_path = metadata.get("root_path", "")
            if root_path.startswith("/"):
                metadata["root_path"] = root_path.lstrip("/")
                changed = True

        # 校验：work_dir 为空或包含 .. 时拒绝
        if metadata.get("work_dir", "") == "":
            raise ValueError(
                f"沙箱实例 {instance.id} ({instance.name}) 的 work_dir 为空，无法迁移"
            )
        if ".." in metadata.get("work_dir", ""):
            raise ValueError(
                f"沙箱实例 {instance.id} ({instance.name}) 的 work_dir 包含 ..，路径不安全"
            )
        if instance.type in ("localsystem", "remotesystem"):
            if metadata.get("root_path", "") == "":
                raise ValueError(
                    f"沙箱实例 {instance.id} ({instance.name}) 的 root_path 为空，无法迁移"
                )
            if ".." in metadata.get("root_path", ""):
                raise ValueError(
                    f"沙箱实例 {instance.id} ({instance.name}) 的 root_path 包含 ..，路径不安全"
                )

        if changed:
            instance.metadata = metadata
            instance.save(update_fields=["metadata"])
