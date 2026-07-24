# Config File Mapping

用户主入口使用 `config_files`，skill 内部再转换为 `config_targets`。

`Kconfig` / `Kconfig.*` 属于源码配置定义文件，直接按原路径应用到目标仓库，不参与映射。
只有 `*defconfig`、`*.config`、`*.cfg` 这类配置产物文件才参与 `config_files -> config_targets` 映射。

## User-facing input

```json
{
  "config_files": [
    "/path/to/target_repo/config.aarch64",
    "/path/to/target_repo/config.aarch64-64k"
  ]
}
```

## Internal mapping rule

如果当前 patch 只涉及一个需要映射的源 defconfig/config 文件：

```json
{
  "arch/arm64/configs/openeuler_defconfig": [
    "/path/to/target_repo/config.aarch64",
    "/path/to/target_repo/config.aarch64-64k"
  ]
}
```

如果 patch 涉及多个需要映射的源 defconfig/config 文件且无法唯一映射，停止并返回 `config-mapping-required`。

## Validation model

config 校验不要求原 defconfig 路径保留；但 patch 中新增的配置行、注释、空行和分组标题都必须出现在映射目标文件中，patch 中删除的对应行也必须消失。
这条规则是严格文本校验，不再忽略注释分组、空行或段落边界差异。

通过：

- `config-mapped-equivalent`

失败：

- `config-mapped-incomplete`
- `config-target-missing`
- `config-unmapped`

## Notes

- `Kconfig` 改动永远直接应用，不要求用户提供映射
- `config_files` 可以是绝对路径或相对路径
- 入口会规范化路径
- 校验时会把 repo 内绝对路径转换成 repo-relative 路径
