# Troubleshooting

## SSH or sudo fails
- Confirm the host is reachable with `ssh <host> true`.
- Configure SSH keys in `~/.ssh/config`.
- Ensure the remote user can run `sudo -n true` without an interactive password.

## KVM or libvirt unavailable
- `doctor` requires `/dev/kvm`, `virsh`, and `virt-install`.
- On Debian/Ubuntu hosts, install `qemu-kvm libvirt-daemon-system virtinst`.
- On RPM hosts, install `qemu-kvm libvirt virt-install`.

## No cloud-init seed tool
Install one of `cloud-localds`, `genisoimage`, or `mkisofs` on the remote host.

## No VM IP address
- Confirm the selected libvirt network is active.
- Run `remote-vm list-networks --host <host>`.
- Some networks may not expose DHCP leases; use the VM console or a bridge with
  predictable DHCP if `domifaddr --source lease` returns empty.

## Catalog image unavailable
Run `remote-vm image-info --os <id>`. If a built-in URL is marked unavailable,
use a mirror with:

```bash
remote-vm create --host build01 --os custom --image-url https://mirror/image.qcow2
```
