## Summary
Customizable management command formatters: allow a management command to control how its help text is formatted.

## Description
When a management command defines a multi-line `help` string, the `help` output collapses the line breaks and indentation into one wrapped paragraph.

Example command:

```python
class Command(BaseCommand):
	help = '''
	Import a contract from tzkt.
	Example usage:
		./manage.py tzkt_import 'Tezos Mainnet' KT1HTDtMBRCKoNHjfWEEvXneGQpCfPAt6BRe
	'''
```

**Actual output:**

```
$ ./manage.py help tzkt_import
usage: manage.py tzkt_import [-h] [--api API] [--version] [-v {0,1,2,3}] [--settings SETTINGS]
							 [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color]
							 [--skip-checks]
							 blockchain target
Import a contract from tzkt Example usage: ./manage.py tzkt_import 'Tezos Mainnet'
KT1HTDtMBRCKoNHjfWEEvXneGQpCfPAt6BRe
positional arguments:
 blockchain			Name of the blockchain to import into
 target				Id of the contract to import
```

**Expected output:**

```
$ ./manage.py help tzkt_import
usage: manage.py tzkt_import [-h] [--api API] [--version] [-v {0,1,2,3}] [--settings SETTINGS]
							 [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color]
							 [--skip-checks]
							 blockchain target
Import a contract from tzkt 
Example usage: 
	./manage.py tzkt_import 'Tezos Mainnet' KT1HTDtMBRCKoNHjfWEEvXneGQpCfPAt6BRe
positional arguments:
 blockchain			Name of the blockchain to import into
 target				Id of the contract to import
```

## Product version
Not provided in the original request.

## Rationale
The help output does not keep the layout the command author wrote. Line breaks and indentation are lost, so structured content such as an "Example usage" section runs into the description and becomes hard to read. The example command is also split across two lines.

## Use case or scenario
A developer writes a custom management command (here, `tzkt_import`, which imports a contract from tzkt). The developer adds a help text with a short description and an indented example invocation. Users who run `./manage.py help tzkt_import` should see the description, the "Example usage:" label and the indented example command on separate lines, as written.

## Possible solution
The title suggests making the formatter used by management commands customizable. A command could then choose a formatter that keeps the line breaks and indentation of its `help` text. The original request gives no further detail.