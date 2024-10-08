# Changelog

<!--next-version-placeholder-->

## v1.4.8 (2024-09-03)
### Fix
* **messages:** Check for invalid key ([`3be020b`](https://github.com/xevg/imessagedb/commit/3be020ba3156ca8bf9444ae8fb9d69a9f533fbb9))
* **messages:** Check for invalid key ([`4cb3d7e`](https://github.com/xevg/imessagedb/commit/4cb3d7ee783408b13071e286926287d9576e03a3))

## v1.4.7 (2024-02-17)


## v1.4.6 (2023-11-17)


## v1.4.5 (2023-11-17)


## v1.4.4 (2023-07-08)


## v1.4.3 (2023-06-05)


## v1.4.2 (2023-05-30)
### Fix
* **text:** Fix labeling of sender ([`f04f0de`](https://github.com/xevg/imessagedb/commit/f04f0de59ffd1ed81f48ee9194d72fd8290dd677))

## v1.4.1 (2023-05-26)
### Fix
* **html:** Fix a typo and an oversight ([`39d1082`](https://github.com/xevg/imessagedb/commit/39d10828fc44ff9744424bd6f7a77c4e7323489e))

## v1.4.0 (2023-05-26)
### Feature
* **html:** Add pagination of the html output ([`d2f1d19`](https://github.com/xevg/imessagedb/commit/d2f1d19ebc7b5a417d87c466bc7f0da9fbb81765))

## v1.3.4 (2023-05-25)
### Fix
* **main:** Change the default directory from /tmp to $HOME ([`232cf29`](https://github.com/xevg/imessagedb/commit/232cf29ef2ade339c4f75f7826123c03f86f0d68))

## v1.3.3 (2023-05-24)
### Fix
* **html:** Fix indexing error ([`162c8bf`](https://github.com/xevg/imessagedb/commit/162c8bf92071e42a93a557b04feaa2c00a548836))

## v1.3.2 (2023-05-24)
### Fix
* Updated the requirements ([`ba0bea8`](https://github.com/xevg/imessagedb/commit/ba0bea8bd86ec11e40afbecb569e23b713707aef))

## v1.3.1 (2023-05-20)
### Fix
* **text:** Add the person's name to the reply text ([`aa9dc9e`](https://github.com/xevg/imessagedb/commit/aa9dc9e5f6cb4871ba5c5c8d7f28e610b77b5725))

## v1.3.0 (2023-05-20)
### Feature
* Add the --chat option to display chats as well as individual messages ([`a739bd1`](https://github.com/xevg/imessagedb/commit/a739bd12bfe76d32cd13f7ab8e37c44539aa4e81))

### Fix
* **message:** Change type hints ([`1c1c4aa`](https://github.com/xevg/imessagedb/commit/1c1c4aa9a16d15a69f2de48175f82d800c210cc7))

## v1.2.13 (2023-05-19)
### Documentation
* Fix the changelog ([`323704b`](https://github.com/xevg/imessagedb/commit/323704b45200d9e51a386f8ee59d450a85e86698))

## v1.2.12 (2023-05-19)
### Feature

* **handles:** add --get_handles option to display the list of handles in the database ([`53194b9`](https://github.com/xevg/imessagedb/commit/53194b965dfb85a503748c79579f1048608aa020))
 
* **chats:** add --get_chats option to display the list of chats in the database ([`2321eee`](https://github.com/xevg/imessagedb/commit/2321eee149b53ba28b5358e380d9a19b08beaa8f))


### Fix

* **main:** change how to add a person ([`c40cbe9`](https://github.com/xevg/imessagedb/commit/c40cbe972a37bbb27d28ca967a5a8dd9ce9c9786))

* **attachments:** skip collecting attachments when 'skip attachments' is set ([`6a78545`](https://github.com/xevg/imessagedb/commit/6a785459cefacfb96c7832270b49fc27c1333cbc))

* **chats:** Changed the output of the chats and updated the documentation ([`877fd81`](https://github.com/xevg/imessagedb/commit/877fd8172038e16300b10a23db4907df2573c565))
 
### Refactor

* **main:** change the structure to allow for general database queries ([`f8ce903`](https://github.com/xevg/imessagedb/commit/f8ce9031963f9dad07f3eb9aa2af9cc714c9ebcd))


## v1.2.11 (2023-05-18)
### Documentation
* Added example output ([`619f120`](https://github.com/xevg/imessagedb/commit/619f12093140ad369dd952c82d4daa8a3a46511d))

## v1.2.10 (2023-05-18)
### Documentation
* Update the readme file with --version ([`e8e1689`](https://github.com/xevg/imessagedb/commit/e8e1689c5622e63cb5f4556663a6b0733f544d58))

## v1.2.9 (2023-05-18)
### Documentation
* Update the readme file with --version and removed old docs ([`be28241`](https://github.com/xevg/imessagedb/commit/be282410fdca1ffd15838eb928b3273f3448ca93))

## v1.2.8 (2023-05-18)
### Fix
* Save the dates for each edit ([`f22e599`](https://github.com/xevg/imessagedb/commit/f22e599d59dcc1041ef66b6a4780f0ef63ac7ab5))
* **html:** Move regexp compiles around, fix some hints, fixed color error ([`63b949f`](https://github.com/xevg/imessagedb/commit/63b949fae7dc4b71b1d765aa88c5b4950273c772))

### Documentation
* **attachments:** Documentation changes ([`6150d6b`](https://github.com/xevg/imessagedb/commit/6150d6b5d2aeabe5c6ceca1122a76e171c0d231c))

## v1.2.7 (2023-05-18)
### Fix
* Remove personal information from the template config file ([`9f7f258`](https://github.com/xevg/imessagedb/commit/9f7f2581163f6d5efd7db20f7c25587ace8beb7f))

## v1.2.6 (2023-05-18)
### Fix
* Add --version and the imessagedb script ([`59f9de4`](https://github.com/xevg/imessagedb/commit/59f9de47c0016f3ac6d4013629af65927d347347))
* Add --version and the imessagedb script ([`b66d6c0`](https://github.com/xevg/imessagedb/commit/b66d6c03da1992b87aee443583aa4c805de092a1))
* Add --version and the imessagedb script ([`53c0f0d`](https://github.com/xevg/imessagedb/commit/53c0f0db5899ce08f997d3a12976d576aff38faf))

## v1.2.5 (2023-05-18)
### Fix
* **attachment:** Fix attachment test to run on github ([`56897b6`](https://github.com/xevg/imessagedb/commit/56897b692ebc7bcae99ecee8267c412820033790))

## v1.2.4 (2023-05-18)


## v1.2.3 (2023-05-17)


## v1.2.2 (2023-05-17)


## v1.0.1 (09/05/2023)

- First public release of `imessagedb`!
- 
## v0.1.0 (09/05/2023)

- First release of `imessagedb`!