
import pymongo
import sys

from bson import ObjectId
from db import tagdb as db
from .tagStatistics import getPopularTags, getCommonTags, updateTagSearch
from spiders import dispatch_no_expand
from utils.exceptions import UserError

def listVideoQuery(query_str, page_idx, page_size, order = 'latest', user_language = 'CHS'):
	if order not in ['latest', 'oldest', 'video_latest', 'video_oldest'] :
		raise UserError('INCORRECT_ORDER')
	query_obj, tag_ids = db.compile_query(query_str)
	updateTagSearch(tag_ids)
	try :
		result = db.retrive_items(query_obj)
		if order == 'latest':
			result = result.sort([("meta.created_at", -1)])
		if order == 'oldest':
			result = result.sort([("meta.created_at", 1)])
		if order == 'video_latest':
			result = result.sort([("item.upload_time", -1)])
		if order == 'video_oldest':
			result = result.sort([("item.upload_time", 1)])
		ret = result.skip(page_idx * page_size).limit(page_size)
		count = ret.count()
		videos = [item for item in ret]
	except pymongo.errors.OperationFailure as ex:
		if '$not' in str(ex) :
			raise UserError('FAILED_NOT_OP')
		else :
			print('Unknown error in query: \"%s\"' % query_str, file = sys.stderr)
			print(ex, file = sys.stderr)
			raise UserError('FAILED_UNKNOWN')
	return videos, getCommonTags(user_language, videos), count

def listVideo(page_idx, page_size, order = 'latest', user_language = 'CHS'):
	if order not in ['latest', 'oldest', 'video_latest', 'video_oldest'] :
		raise UserError('INCORRECT_ORDER')
	result = db.retrive_items({})
	if order == 'latest':
		result = result.sort([("meta.created_at", -1)])
	if order == 'oldest':
		result = result.sort([("meta.created_at", 1)])
	if order == 'video_latest':
		result = result.sort([("item.upload_time", -1)])
	if order == 'video_oldest':
		result = result.sort([("item.upload_time", 1)])
	return result.skip(page_idx * page_size).limit(page_size), getPopularTags(user_language)

def listMyVideo(page_idx, page_size, user, order = 'latest'):
	if order not in ['latest', 'oldest', 'video_latest', 'video_oldest'] :
		raise UserError('INCORRECT_ORDER')
	result = db.retrive_items({'meta.created_by': ObjectId(user['_id'])})
	if order == 'latest':
		result = result.sort([("meta.created_at", -1)])
	if order == 'oldest':
		result = result.sort([("meta.created_at", 1)])
	if order == 'video_latest':
		result = result.sort([("item.upload_time", -1)])
	if order == 'video_oldest':
		result = result.sort([("item.upload_time", 1)])
	return result.skip(page_idx * page_size).limit(page_size)
