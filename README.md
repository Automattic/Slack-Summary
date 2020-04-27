# Slack Summary

The purpose of the Slack Summary is to distill a given slack thread to a handful of key messages. It is based on [@charlesearl's Data Science trial](https://datap2.wordpress.com/2015/09/20/charles-earl-trial-project-slack-summarization-bot/) and
uses [extractive summarization](https://towardsdatascience.com/a-quick-introduction-to-text-summarization-in-machine-learning-3d27ccf18a9f) -- an approach in which
the most salient messages are pulled from a thread -- to build a gist of the thread based on the highlights. 

It is a fork of the [Summarize It!](https://github.com/yask123/Summarize-it) with some additional pre- and post- processing to make navigating the 
most salient messages of the thread easier.

## Installing and running

After you have cloned the repository, you can build and then test it by running

```
make clean check
```

To test that it properly connects to Slack you can create a token at `https://api.slack.com/web` 


Then edit the `summarizer/config.py` file, replacing the `<Your Token Here>` with your token

```
KEYS = {'slack': '<Your Token Here>'}
```


Then edit `ts_config.py` file to adjust the debugging options

     SUMMARY_INTERVALS = [{'days': 5, 'size': 2}, ]
     TS_DEBUG = True
     TS_LOG = "./ts_summ.log"
     DEBUG=True
     LOG_FILE="./summary.log"

Here the `LOG_FILE` stores where notices of users accessing the server is stored and the
value of `DEBUG` determines if detailed logging is stored.

The server is executed by running

    python manage.py main --log-level DEBUG
	
You can get a canned test summarization by starting the server and sending the `slacktest` command

```
> curl http://localhost:8193/slacktest                                                                                                                                                                                          (/Users/charlescearl/Projects/elfbot/conda_env)
*Chat Summary:*
 Summary is @Thu-Sep-9-2015 18:31:29 <@U029LMSEC>: i’m wondering if in the future we would like some kind of heatmap option for homepage, like `wpcom_homepage_link_click` with properties: signup_top, signup_bottom, xyz, abc, etc
@Thu-Sep-9-2015 18:34:01 <@U029LMSEC>: &gt; If there are 2 buttons on the page going to the same link, you could differentiate them by putting in a query parameter to the url
@Thu-Sep-9-2015 22:49:42 <@U03CGFPKV>: once we have user properties, we should be able to tell if a specific user is a paid user at a given point in time
```

To explore more complete examples, you provide the channel id and text specifying how many minutes, hours, days or weeks prior to the current time the summary should include. For instance, highlights of the last two weeks of the data 
science channel:


```

> curl http://localhost:8193/slack -H "Content-Type: application/json" -d '{"text": "-2 weeks", "channel_id": "C5RPL6XBP"}'                                                                                                     (/Users/charlescearl/Projects/elfbot/conda_env)
*Chat Summary:*
 Summary is @Thu-Apr-4-2020 00:19:32 <@U0B3FSU04>: Howdy <@U07B0622C>! I’m having some trouble running the <https://github.com/Automattic/data-science/blob/master/lab/geo_experiments/resources/setup_summary.ipynb|GeoX setup_summary notebook> and received some errors like missing `rpy2` . I’m running into <https://mc.a8c.com/pb/249ab/#plain|additional errors> after `pip install rpy2`. I tried...
@Thu-Apr-4-2020 15:33:34 <@U07B7E30F>: Welcome to our <#C5RPL6XBP|data-science> channel! This is a great place to chat about all things data science, and to get help with anything related to the data-science repo.
@Thu-Apr-4-2020 20:36:16 <@UNY0MP75Z>: Hi. I heard that there is a a8c funnel analysis tool and was wondering if anyone could point me to more information about it


```

## Using Summarize It plugin with slack

Let's assume that that plugin is named <b>summary</b>. The plugin supports a small
command line syntax with allows specification of the previous window of time to look
back. Currently this can be specified in `minutes, hours, days, or weeks`. 


The summarizer application takes as input a look-back time window on which to construct the summary. For example

```
/summary -5 days
```

generates a summary that includes messages from five days ago up to the present time.

The command syntax formally is

```
::= /summary -
::= minutes|hours|days|weeks
::= integer
```

so

```
/summary -5 hours
/summary -30 minutes
```

means "generate a summary covering the last 5 hours" and "generate a summary covering the last 30 minutes" respectively.



So to get the key messages from the last 5 days:

```
   /summary 5 days
```

Or to get a summary of the important messages over the last two weeks

```
   /summary 2 weeks
```
