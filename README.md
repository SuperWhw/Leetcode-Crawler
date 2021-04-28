# Leetcode-Crawler


## Support functions

- [x] Crawl all your submissions to file
- [x] Build contests info table to file
- [x] Post contest summary on leetcode discussion
- [ ] User contest history profile


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

### 3. Post contest summary on leetcode discussion

For example, if you want to post weekly-contest-238, run:

```shell
python main.py -u USERNAME -p PASSWORD --post_url https://leetcode.com/discuss/general-discussion/1175023/weekly-contest-238
```



## Sceenshot

### Submission table

![image](https://user-images.githubusercontent.com/37525190/116203267-17a71880-a76e-11eb-80e8-6a6eb3bd526b.png)

### Contests info table

![image](https://user-images.githubusercontent.com/37525190/116203508-58069680-a76e-11eb-8907-6df45eb0469a.png)

### Generated contest summary

![image](https://user-images.githubusercontent.com/37525190/116203728-956b2400-a76e-11eb-9496-516efdd406aa.png)
