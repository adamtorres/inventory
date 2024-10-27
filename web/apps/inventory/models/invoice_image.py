"""
One suggestion of storing images in a database was to use django-storages and point to S3.
It claimed it could be done with basic django form fields with the actual saving of files handled automatically.
https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html

This is a local S3-compatible storage implementation.
https://min.io/docs/minio/kubernetes/upstream/index.html?ref=docs-redirect
Also:
https://github.com/getmoto/moto

Sysco invoices are generally 1 or 2 pages
USFood invoices are at least 3 pages with the 1st having most of the items and the 2nd having the delivery fee.
  Whole frozen turkeys showed up on the 3rd page once.
Gem invoices are split into types
  Shipping has no prices.
  invoice has prices but shows up in email - need the general timing of that.
  payment has no items but invoice totals.  Not sure this is needed here.
broulims are very inconsistent in size and have very cryptic item names.
  Long receipts are likely split in two or more images
"""