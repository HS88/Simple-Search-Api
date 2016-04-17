from __future__ import unicode_literals

from django.db import models


class Search(models.Model):

    @staticmethod
    def testMethod():
    	return "result"

    class Meta:
        verbose_name_plural = 'Search'