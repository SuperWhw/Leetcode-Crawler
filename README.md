# Leetcode-Crawler


## Support functions

- Crawl all your submissions to file
- Build contests info table to file
- Post useful information on leetcode discussion 

## How to use

First of all, you should have a leetcode account. Remember the correct username and password.

### 1. Crawl submissions to file

Simply run:

```shell
python main.py -u USERNAME -p PASSWORD -gs
```

or give specific saving path:

```shell
python main.py -u USERNAME -p PASSWORD -gs -ssp YOUR_SAVE_PATH
```

### 2. Build contests info table to file

Run:

```shell
python main.py -u USERNAME -p PASSWORD -bt --end END_CONTEST
```

Default start contest is weekly-contest-200, if you want to build from a different contest number, add `--start START_CONTEST` to the command line.

If you want to rewrite contest data which already exists, add `--rewrite`, and you could also give a specific saving path:

```shell
python main.py -bt \
-u USERNAME \
-p PASSWORD \
--start START_CONTEST \
--end END_CONTEST \
--rewrite \
--save_path SAVE_PATH
```

### 3. Post info on leetcode discussion

For example, if you want to post weekly-contest-238, run:

```shell
python main.py -u USERNAME -p PASSWORD --post_url https://leetcode.com/discuss/general-discussion/1175023/weekly-contest-238
```
