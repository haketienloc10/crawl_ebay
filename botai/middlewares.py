# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import random

from scrapy import signals

# proxy middleware
import re
import random
import base64
import logging

log = logging.getLogger('scrapy.proxies')

class Mode:
    RANDOMIZE_PROXY_EVERY_REQUESTS, RANDOMIZE_PROXY_ONCE, SET_CUSTOM_PROXY = range(3)
# 


class BotaiSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class BotaiDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class UserAgentMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self,user_agent):
        self.useragent = user_agent

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls(
            user_agent=crawler.settings.get("USERAGENT")
        )
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        UserAgent = random.choice(self.useragent)
        request.headers["User-Agent"] = UserAgent
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


# class RandomProxy(object):
#     def __init__(self, settings):
#         self.proxy_list = settings.get('PROXY_LIST')

#     @classmethod
#     def from_crawler(cls, crawler):
#         return cls(crawler.settings)

#     def process_request(self, request, spider):
#         proxy = random.choice(self.proxy_list)
#         print((proxy['user_pass']))
#         splash = request.meta.get("splash")
#         if splash is not None:
#             splash['args']['proxy'] = "http://%s" % proxy['ip_port']

#     def process_exception(self, request, exception, spider):
#         pass

class RandomProxy(object):
    def __init__(self, settings):
        self.mode = settings.get('PROXY_MODE')
        self.proxy_list = settings.get('PROXY_LIST')
        self.chosen_proxy = ''

        if self.mode == Mode.RANDOMIZE_PROXY_EVERY_REQUESTS or self.mode == Mode.RANDOMIZE_PROXY_ONCE:
            if self.proxy_list is None:
                raise KeyError('PROXY_LIST setting is missing')
            self.proxies = {}
            # fin = open(self.proxy_list)
            for proxy in self.proxy_list:
                parts = re.match('(\w+://)([^:]+?:[^@]+?@)?(.+)', proxy)
                if not parts:
                    continue

                # Cut trailing @
                if parts.group(2):
                    user_pass = parts.group(2)[:-1]
                else:
                    user_pass = ''

                self.proxies[proxy] = user_pass

            if self.mode == Mode.RANDOMIZE_PROXY_ONCE:
                self.chosen_proxy = random.choice(list(self.proxies.keys()))
        elif self.mode == Mode.SET_CUSTOM_PROXY:
            custom_proxy = settings.get('CUSTOM_PROXY')
            self.proxies = {}
            parts = re.match('(\w+://)([^:]+?:[^@]+?@)?(.+)', custom_proxy)
            if not parts:
                raise ValueError('CUSTOM_PROXY is not well formatted')

            if parts.group(2):
                user_pass = parts.group(2)[:-1]
            else:
                user_pass = ''

            self.proxies[custom_proxy] = user_pass
            self.chosen_proxy = custom_proxy

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        splash = request.meta.get("splash")
        # Don't overwrite with a random one (server-side state for IP)
        if 'proxy' in request.meta:
            if request.meta["exception"] is False:
                return
        request.meta["exception"] = False
        if len(self.proxies) == 0:
            raise ValueError('All proxies are unusable, cannot proceed')

        if self.mode == Mode.RANDOMIZE_PROXY_EVERY_REQUESTS:
            proxy_address = random.choice(list(self.proxies.keys()))
        else:
            proxy_address = self.chosen_proxy

        print("proxy_address: %s" % proxy_address)
        proxy_user_pass = self.proxies[proxy_address]

        if splash is not None:
            # print(splash)
            

            if proxy_user_pass:
                splash['args']['proxy'] = proxy_address
                # basic_auth = base64.b64encode(proxy_user_pass.encode()).decode()
                # basic_auth = base64.encodestring(proxy_user_pass)
                # splash['Proxy-Authorization'] = 'Basic ' + basic_auth
                # print("splash['Proxy-Authorization']']: %s" % splash['Proxy-Authorization'])
            else:
                splash['args']['proxy'] = proxy_address
                log.debug('Proxy user pass not found')
        
        log.debug('Using proxy <%s>, %d proxies left' % (proxy_address, len(self.proxies)))

    def process_exception(self, request, exception, spider):
        if 'proxy' not in request.meta:
            return
        if self.mode == Mode.RANDOMIZE_PROXY_EVERY_REQUESTS or self.mode == Mode.RANDOMIZE_PROXY_ONCE:
            proxy = request.meta['proxy']
            try:
                if len(self.proxies) > 1:
                    del self.proxies[proxy]
                else:
                    log.warning('Only one proxy, Don\'t remove it')
            except KeyError:
                pass
            request.meta["exception"] = True
            if self.mode == Mode.RANDOMIZE_PROXY_ONCE:
                self.chosen_proxy = random.choice(list(self.proxies.keys()))
            log.info('Removing failed proxy <%s>, %d proxies left' % (
                proxy, len(self.proxies)))