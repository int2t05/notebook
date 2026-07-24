#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spark表达式测试SQL生成脚本
根据输入的CSV文件，为每个Spark表达式生成19种数据类型的测试SQL
"""

import csv
import re
import os
import sys

# 数据类型到列名的映射
TYPE_TO_COLUMN = {
    'BOOLEAN': 'c_bool',
    'BYTE': 'c_byte',
    'SHORT': 'c_short',
    'INT': 'c_int',
    'LONG': 'c_long',
    'FLOAT': 'c_float',
    'DOUBLE': 'c_double',
    'STRING': 'c_string',
    'CHAR': 'c_char',
    'VARCHAR': 'c_varchar',
    'NULL': 'c_none',
    'DATE': 'c_date',
    'TIMESTAMP': 'c_timestamp',
    'DECIMAL64': 'c_deci64',
    'DECIMAL128': 'c_decimal128',
    'BINARY': 'c_binary',
    'ARRAY': 'c_array',
    'MAP': 'c_map',
    'STRUCT(ROW)': 'c_struct'
}

# 数据类型列的顺序（从CSV表头）
TYPE_COLUMNS = [
    'BOOLEAN', 'BYTE', 'SHORT', 'INT', 'LONG', 'FLOAT', 'DOUBLE',
    'STRING', 'CHAR', 'VARCHAR', 'NULL', 'DATE', 'TIMESTAMP',
    'DECIMAL64', 'DECIMAL128', 'BINARY', 'ARRAY', 'MAP', 'STRUCT(ROW)'
]

# ============================================================
# 函数签名配置表
# 占位符: {col}=列名
# 不含 {col} 的模板表示SQL不依赖列类型（如无参数函数）
# 新增函数只需在字典中添加一行
# ============================================================

FUNC_SQL_TEMPLATES = {
    # --- 无参数函数 ---
    'e': 'SELECT e() FROM sve_exp_operator_panoramic;',
    'input_file_block_length': 'SELECT input_file_block_length() FROM sve_exp_operator_panoramic;',
    'input_file_block_start': 'SELECT input_file_block_start() FROM sve_exp_operator_panoramic;',
    'input_file_name': 'SELECT input_file_name() FROM sve_exp_operator_panoramic;',
    'monotonically_increasing_id': 'SELECT monotonically_increasing_id() FROM sve_exp_operator_panoramic;',
    'now': 'SELECT now() FROM sve_exp_operator_panoramic;',
    'pi': 'SELECT pi() FROM sve_exp_operator_panoramic;',
    'rand': 'SELECT rand() FROM sve_exp_operator_panoramic;',
    'random': 'SELECT random() FROM sve_exp_operator_panoramic;',
    'randn': 'SELECT randn() FROM sve_exp_operator_panoramic;',
    'spark_partition_id': 'SELECT spark_partition_id() FROM sve_exp_operator_panoramic;',
    'uuid': 'SELECT uuid() FROM sve_exp_operator_panoramic;',
    'version': 'SELECT version() FROM sve_exp_operator_panoramic;',
    'current_catalog': 'SELECT current_catalog() FROM sve_exp_operator_panoramic;',
    'current_database': 'SELECT current_database() FROM sve_exp_operator_panoramic;',
    'current_timezone': 'SELECT current_timezone() FROM sve_exp_operator_panoramic;',
    'current_date': 'SELECT current_date() FROM sve_exp_operator_panoramic;',
    'current_timestamp': 'SELECT current_timestamp() FROM sve_exp_operator_panoramic;',
    'localtimestamp': 'SELECT localtimestamp() FROM sve_exp_operator_panoramic;',
    'make_date': 'SELECT make_date(2023, 1, 1) FROM sve_exp_operator_panoramic;',
    'make_timestamp': 'SELECT make_timestamp(2023, 1, 1, 0, 0, 0) FROM sve_exp_operator_panoramic;',

    # --- 窗口函数（无参数） ---
    'cume_dist': 'SELECT cume_dist() OVER (ORDER BY c_int) FROM sve_exp_operator_panoramic;',
    'dense_rank': 'SELECT dense_rank() OVER (ORDER BY c_int) FROM sve_exp_operator_panoramic;',
    'ntile': 'SELECT ntile(4) OVER (ORDER BY c_int) FROM sve_exp_operator_panoramic;',
    'percent_rank': 'SELECT percent_rank() OVER (ORDER BY c_int) FROM sve_exp_operator_panoramic;',
    'rank': 'SELECT rank() OVER (ORDER BY c_int) FROM sve_exp_operator_panoramic;',
    'row_number': 'SELECT row_number() OVER (ORDER BY c_int) FROM sve_exp_operator_panoramic;',

    # --- 单参数函数 ---
    'abs': 'SELECT abs({col}) FROM sve_exp_operator_panoramic;',
    'acos': 'SELECT acos({col}) FROM sve_exp_operator_panoramic;',
    'array_distinct': 'SELECT array_distinct({col}) FROM sve_exp_operator_panoramic;',
    'array_length': 'SELECT array_length({col}) FROM sve_exp_operator_panoramic;',
    'array_max': 'SELECT array_max({col}) FROM sve_exp_operator_panoramic;',
    'array_min': 'SELECT array_min({col}) FROM sve_exp_operator_panoramic;',
    'array_size': 'SELECT array_size({col}) FROM sve_exp_operator_panoramic;',
    'array_sort': 'SELECT array_sort({col}) FROM sve_exp_operator_panoramic;',
    'asin': 'SELECT asin({col}) FROM sve_exp_operator_panoramic;',
    'atan': 'SELECT atan({col}) FROM sve_exp_operator_panoramic;',
    'base64': 'SELECT base64({col}) FROM sve_exp_operator_panoramic;',
    'bin': 'SELECT bin({col}) FROM sve_exp_operator_panoramic;',
    'bit_length': 'SELECT bit_length({col}) FROM sve_exp_operator_panoramic;',
    'btrim': 'SELECT btrim({col}) FROM sve_exp_operator_panoramic;',
    'cbrt': 'SELECT cbrt({col}) FROM sve_exp_operator_panoramic;',
    'cardinality': 'SELECT cardinality({col}) FROM sve_exp_operator_panoramic;',
    'char_length': 'SELECT char_length({col}) FROM sve_exp_operator_panoramic;',
    'character_length': 'SELECT character_length({col}) FROM sve_exp_operator_panoramic;',
    'cosh': 'SELECT cosh({col}) FROM sve_exp_operator_panoramic;',
    'cos': 'SELECT cos({col}) FROM sve_exp_operator_panoramic;',
    'crc32': 'SELECT crc32({col}) FROM sve_exp_operator_panoramic;',
    'dayofmonth': 'SELECT dayofmonth({col}) FROM sve_exp_operator_panoramic;',
    'dayofweek': 'SELECT dayofweek({col}) FROM sve_exp_operator_panoramic;',
    'dayofyear': 'SELECT dayofyear({col}) FROM sve_exp_operator_panoramic;',
    'day': 'SELECT day({col}) FROM sve_exp_operator_panoramic;',
    'degrees': 'SELECT degrees({col}) FROM sve_exp_operator_panoramic;',
    'exp': 'SELECT exp({col}) FROM sve_exp_operator_panoramic;',
    'flatten': 'SELECT flatten({col}) FROM sve_exp_operator_panoramic;',
    'hash': 'SELECT hash({col}) FROM sve_exp_operator_panoramic;',
    'hex': 'SELECT hex({col}) FROM sve_exp_operator_panoramic;',
    'hour': 'SELECT hour({col}) FROM sve_exp_operator_panoramic;',
    'initcap': 'SELECT initcap({col}) FROM sve_exp_operator_panoramic;',
    'isnan': 'SELECT isnan({col}) FROM sve_exp_operator_panoramic;',
    'isnotnull': 'SELECT isnotnull({col}) FROM sve_exp_operator_panoramic;',
    'isnull': 'SELECT isnull({col}) FROM sve_exp_operator_panoramic;',
    'lcase': 'SELECT lcase({col}) FROM sve_exp_operator_panoramic;',
    'last_day': 'SELECT last_day({col}) FROM sve_exp_operator_panoramic;',
    'len': 'SELECT len({col}) FROM sve_exp_operator_panoramic;',
    'length': 'SELECT length({col}) FROM sve_exp_operator_panoramic;',
    'ln': 'SELECT ln({col}) FROM sve_exp_operator_panoramic;',
    'log10': 'SELECT log10({col}) FROM sve_exp_operator_panoramic;',
    'log2': 'SELECT log2({col}) FROM sve_exp_operator_panoramic;',
    'log': 'SELECT log({col}) FROM sve_exp_operator_panoramic;',
    'lower': 'SELECT lower({col}) FROM sve_exp_operator_panoramic;',
    'ltrim': 'SELECT ltrim({col}) FROM sve_exp_operator_panoramic;',
    'map_keys': 'SELECT map_keys({col}) FROM sve_exp_operator_panoramic;',
    'map_values': 'SELECT map_values({col}) FROM sve_exp_operator_panoramic;',
    'md5': 'SELECT md5({col}) FROM sve_exp_operator_panoramic;',
    'minute': 'SELECT minute({col}) FROM sve_exp_operator_panoramic;',
    'month': 'SELECT month({col}) FROM sve_exp_operator_panoramic;',
    'negative': 'SELECT negative({col}) FROM sve_exp_operator_panoramic;',
    'octet_length': 'SELECT octet_length({col}) FROM sve_exp_operator_panoramic;',
    'positive': 'SELECT positive({col}) FROM sve_exp_operator_panoramic;',
    'quarter': 'SELECT quarter({col}) FROM sve_exp_operator_panoramic;',
    'radians': 'SELECT radians({col}) FROM sve_exp_operator_panoramic;',
    'reverse': 'SELECT reverse({col}) FROM sve_exp_operator_panoramic;',
    'rtrim': 'SELECT rtrim({col}) FROM sve_exp_operator_panoramic;',
    'second': 'SELECT second({col}) FROM sve_exp_operator_panoramic;',
    'sha1': 'SELECT sha1({col}) FROM sve_exp_operator_panoramic;',
    'sha': 'SELECT sha({col}) FROM sve_exp_operator_panoramic;',
    'signum': 'SELECT signum({col}) FROM sve_exp_operator_panoramic;',
    'sign': 'SELECT sign({col}) FROM sve_exp_operator_panoramic;',
    'sinh': 'SELECT sinh({col}) FROM sve_exp_operator_panoramic;',
    'sin': 'SELECT sin({col}) FROM sve_exp_operator_panoramic;',
    'size': 'SELECT size({col}) FROM sve_exp_operator_panoramic;',
    'sort_array': 'SELECT sort_array({col}) FROM sve_exp_operator_panoramic;',
    'sqrt': 'SELECT sqrt({col}) FROM sve_exp_operator_panoramic;',
    'tanh': 'SELECT tanh({col}) FROM sve_exp_operator_panoramic;',
    'tan': 'SELECT tan({col}) FROM sve_exp_operator_panoramic;',
    'to_date': 'SELECT to_date({col}) FROM sve_exp_operator_panoramic;',
    'to_timestamp': 'SELECT to_timestamp({col}) FROM sve_exp_operator_panoramic;',
    'trim': 'SELECT trim({col}) FROM sve_exp_operator_panoramic;',
    'try_to_date': 'SELECT try_to_date({col}) FROM sve_exp_operator_panoramic;',
    'try_to_timestamp': 'SELECT try_to_timestamp({col}) FROM sve_exp_operator_panoramic;',
    'ucase': 'SELECT ucase({col}) FROM sve_exp_operator_panoramic;',
    'unbase64': 'SELECT unbase64({col}) FROM sve_exp_operator_panoramic;',
    'unhex': 'SELECT unhex({col}) FROM sve_exp_operator_panoramic;',
    'unix_date': 'SELECT unix_date({col}) FROM sve_exp_operator_panoramic;',
    'unix_micros': 'SELECT unix_micros({col}) FROM sve_exp_operator_panoramic;',
    'unix_millis': 'SELECT unix_millis({col}) FROM sve_exp_operator_panoramic;',
    'unix_seconds': 'SELECT unix_seconds({col}) FROM sve_exp_operator_panoramic;',
    'upper': 'SELECT upper({col}) FROM sve_exp_operator_panoramic;',
    'weekday': 'SELECT weekday({col}) FROM sve_exp_operator_panoramic;',
    'weekofyear': 'SELECT weekofyear({col}) FROM sve_exp_operator_panoramic;',
    'year': 'SELECT year({col}) FROM sve_exp_operator_panoramic;',
    'xxhash64': 'SELECT xxhash64({col}) FROM sve_exp_operator_panoramic;',

    # --- 单参数聚合函数（直接聚合，不分组） ---
    'avg': 'SELECT avg({col}) FROM sve_exp_operator_panoramic;',
    'count': 'SELECT count({col}) FROM sve_exp_operator_panoramic;',
    'kurtosis': 'SELECT kurtosis({col}) FROM sve_exp_operator_panoramic;',
    'max': 'SELECT max({col}) FROM sve_exp_operator_panoramic;',
    'min': 'SELECT min({col}) FROM sve_exp_operator_panoramic;',
    'skewness': 'SELECT skewness({col}) FROM sve_exp_operator_panoramic;',
    'stddev': 'SELECT stddev({col}) FROM sve_exp_operator_panoramic;',
    'stddev_pop': 'SELECT stddev_pop({col}) FROM sve_exp_operator_panoramic;',
    'stddev_samp': 'SELECT stddev_samp({col}) FROM sve_exp_operator_panoramic;',
    'sum': 'SELECT sum({col}) FROM sve_exp_operator_panoramic;',
    'variance': 'SELECT variance({col}) FROM sve_exp_operator_panoramic;',
    'var_pop': 'SELECT var_pop({col}) FROM sve_exp_operator_panoramic;',
    'var_samp': 'SELECT var_samp({col}) FROM sve_exp_operator_panoramic;',
    'collect_list': 'SELECT collect_list({col}) FROM sve_exp_operator_panoramic;',
    'collect_set': 'SELECT collect_set({col}) FROM sve_exp_operator_panoramic;',

    # --- 两参数函数 ---
    'add_months': "SELECT add_months({col}, 1) FROM sve_exp_operator_panoramic;",
    'aes_decrypt': "SELECT aes_decrypt({col}, 'key') FROM sve_exp_operator_panoramic;",
    'aes_encrypt': "SELECT aes_encrypt({col}, 'key') FROM sve_exp_operator_panoramic;",
    'array_contains': "SELECT array_contains({col}, c_int) FROM sve_exp_operator_panoramic;",
    'array_except': "SELECT array_except({col}, {col}) FROM sve_exp_operator_panoramic;",
    'array_intersect': "SELECT array_intersect({col}, {col}) FROM sve_exp_operator_panoramic;",
    'array_join': "SELECT array_join({col}, ',') FROM sve_exp_operator_panoramic;",
    'array_position': "SELECT array_position({col}, c_int) FROM sve_exp_operator_panoramic;",
    'array_remove': "SELECT array_remove({col}, c_int) FROM sve_exp_operator_panoramic;",
    'array_repeat': "SELECT array_repeat(c_int, 3) FROM sve_exp_operator_panoramic;",
    'array_union': "SELECT array_union({col}, {col}) FROM sve_exp_operator_panoramic;",
    'arrays_overlap': "SELECT arrays_overlap({col}, {col}) FROM sve_exp_operator_panoramic;",
    'atan2': "SELECT atan2({col}, {col}) FROM sve_exp_operator_panoramic;",
    'bit_get': "SELECT bit_get({col}, 1) FROM sve_exp_operator_panoramic;",
    'bround': "SELECT bround({col}, 2) FROM sve_exp_operator_panoramic;",
    'ceil': "SELECT ceil({col}) FROM sve_exp_operator_panoramic;",
    'ceiling': "SELECT ceiling({col}) FROM sve_exp_operator_panoramic;",
    'concat': "SELECT concat({col}, 'a', 'b') FROM sve_exp_operator_panoramic;",
    'contains': "SELECT contains({col}, 'sub') FROM sve_exp_operator_panoramic;",
    'corr': "SELECT corr({col}, {col}) FROM sve_exp_operator_panoramic;",
    'covar_pop': "SELECT covar_pop({col}, {col}) FROM sve_exp_operator_panoramic;",
    'covar_samp': "SELECT covar_samp({col}, {col}) FROM sve_exp_operator_panoramic;",
    'date_add': "SELECT date_add({col}, 1) FROM sve_exp_operator_panoramic;",
    'date_diff': "SELECT date_diff({col}, {col}) FROM sve_exp_operator_panoramic;",
    'date_part': "SELECT date_part('day', {col}) FROM sve_exp_operator_panoramic;",
    'date_sub': "SELECT date_sub({col}, 1) FROM sve_exp_operator_panoramic;",
    'date_trunc': "SELECT date_trunc('day', {col}) FROM sve_exp_operator_panoramic;",
    'datediff': "SELECT datediff({col}, {col}) FROM sve_exp_operator_panoramic;",
    'div': "SELECT div({col}, {col}) FROM sve_exp_operator_panoramic;",
    'element_at': "SELECT element_at({col}, 1) FROM sve_exp_operator_panoramic;",
    'encode': "SELECT encode({col}, 'UTF-8') FROM sve_exp_operator_panoramic;",
    'endswith': "SELECT endswith({col}, 'sub') FROM sve_exp_operator_panoramic;",
    'find_in_set': "SELECT find_in_set('a', c_string) FROM sve_exp_operator_panoramic;",
    'first_value': "SELECT first_value({col}) OVER (ORDER BY c_int) FROM sve_exp_operator_panoramic;",
    'floor': "SELECT floor({col}) FROM sve_exp_operator_panoramic;",
    'format_number': "SELECT format_number({col}, 2) FROM sve_exp_operator_panoramic;",
    'from_csv': "SELECT from_csv({col}, 'a INT') FROM sve_exp_operator_panoramic;",
    'from_utc_timestamp': "SELECT from_utc_timestamp({col}, 'UTC') FROM sve_exp_operator_panoramic;",
    'getbit': "SELECT getbit({col}, 1) FROM sve_exp_operator_panoramic;",
    'histogram_numeric': "SELECT histogram_numeric({col}, 10) FROM sve_exp_operator_panoramic;",
    'hypot': "SELECT hypot({col}, {col}) FROM sve_exp_operator_panoramic;",
    'ifnull': "SELECT ifnull({col}, {col}) FROM sve_exp_operator_panoramic;",
    'instr': "SELECT instr({col}, 'sub') FROM sve_exp_operator_panoramic;",
    'lag': "SELECT lag({col}, 1) OVER (ORDER BY c_int) FROM sve_exp_operator_panoramic;",
    'last_value': "SELECT last_value({col}) OVER (ORDER BY c_int) FROM sve_exp_operator_panoramic;",
    'lead': "SELECT lead({col}, 1) OVER (ORDER BY c_int) FROM sve_exp_operator_panoramic;",
    'left': "SELECT left({col}, 5) FROM sve_exp_operator_panoramic;",
    'levenshtein': "SELECT levenshtein({col}, {col}) FROM sve_exp_operator_panoramic;",
    'locate': "SELECT locate('sub', {col}) FROM sve_exp_operator_panoramic;",
    'lpad': "SELECT lpad({col}, 10, ' ') FROM sve_exp_operator_panoramic;",
    'map_contains_key': "SELECT map_contains_key({col}, c_string) FROM sve_exp_operator_panoramic;",
    'map_from_arrays': "SELECT map_from_arrays({col}, {col}) FROM sve_exp_operator_panoramic;",
    'max_by': "SELECT max_by({col}, {col}) FROM sve_exp_operator_panoramic;",
    'min_by': "SELECT min_by({col}, {col}) FROM sve_exp_operator_panoramic;",
    'mod': "SELECT mod({col}, {col}) FROM sve_exp_operator_panoramic;",
    'months_between': "SELECT months_between({col}, {col}) FROM sve_exp_operator_panoramic;",
    'nanvl': "SELECT nanvl({col}, {col}) FROM sve_exp_operator_panoramic;",
    'next_day': "SELECT next_day({col}, 'Mon') FROM sve_exp_operator_panoramic;",
    'nullif': "SELECT nullif({col}, {col}) FROM sve_exp_operator_panoramic;",
    'nvl': "SELECT nvl({col}, {col}) FROM sve_exp_operator_panoramic;",
    'percentile': "SELECT percentile({col}, 0.5) FROM sve_exp_operator_panoramic;",
    'percentile_approx': "SELECT percentile_approx({col}, 0.5) FROM sve_exp_operator_panoramic;",
    'pmod': "SELECT pmod({col}, {col}) FROM sve_exp_operator_panoramic;",
    'pow': "SELECT pow({col}, 2) FROM sve_exp_operator_panoramic;",
    'power': "SELECT power({col}, 2) FROM sve_exp_operator_panoramic;",
    'regexp_extract_all': "SELECT regexp_extract_all({col}, 'pattern') FROM sve_exp_operator_panoramic;",
    'regexp_like': "SELECT regexp_like({col}, 'pattern') FROM sve_exp_operator_panoramic;",
    'regr_count': "SELECT regr_count({col}, {col}) FROM sve_exp_operator_panoramic;",
    'regr_r2': "SELECT regr_r2({col}, {col}) FROM sve_exp_operator_panoramic;",
    'repeat': "SELECT repeat({col}, 3) FROM sve_exp_operator_panoramic;",
    'right': "SELECT right({col}, 5) FROM sve_exp_operator_panoramic;",
    'round': "SELECT round({col}, 2) FROM sve_exp_operator_panoramic;",
    'rpad': "SELECT rpad({col}, 10, ' ') FROM sve_exp_operator_panoramic;",
    'sequence': "SELECT sequence(1, {col}) FROM sve_exp_operator_panoramic;",
    'session_window': "SELECT session_window({col}, 5) FROM sve_exp_operator_panoramic;",
    'sha2': "SELECT sha2({col}, 256) FROM sve_exp_operator_panoramic;",
    'shiftleft': "SELECT shiftleft({col}, 1) FROM sve_exp_operator_panoramic;",
    'shiftright': "SELECT shiftright({col}, 1) FROM sve_exp_operator_panoramic;",
    'shiftrightunsigned': "SELECT shiftrightunsigned({col}, 1) FROM sve_exp_operator_panoramic;",
    'slice': "SELECT slice({col}, 1, 3) FROM sve_exp_operator_panoramic;",
    'split_part': "SELECT split_part({col}, ',', 1) FROM sve_exp_operator_panoramic;",
    'split': "SELECT split({col}, ',') FROM sve_exp_operator_panoramic;",
    'startswith': "SELECT startswith({col}, 'sub') FROM sve_exp_operator_panoramic;",
    'substr': "SELECT substr({col}, 1, 5) FROM sve_exp_operator_panoramic;",
    'substring': "SELECT substring({col}, 1, 5) FROM sve_exp_operator_panoramic;",
    'to_number': "SELECT to_number({col}, '999.99') FROM sve_exp_operator_panoramic;",
    'to_utc_timestamp': "SELECT to_utc_timestamp({col}, 'UTC') FROM sve_exp_operator_panoramic;",
    'trunc': "SELECT trunc({col}, 'year') FROM sve_exp_operator_panoramic;",
    'try_add': "SELECT try_add({col}, {col}) FROM sve_exp_operator_panoramic;",
    'try_divide': "SELECT try_divide({col}, {col}) FROM sve_exp_operator_panoramic;",
    'try_element_at': "SELECT try_element_at({col}, 1) FROM sve_exp_operator_panoramic;",
    'try_multiply': "SELECT try_multiply({col}, {col}) FROM sve_exp_operator_panoramic;",
    'try_subtract': "SELECT try_subtract({col}, {col}) FROM sve_exp_operator_panoramic;",
    'try_to_number': "SELECT try_to_number({col}, '999.99') FROM sve_exp_operator_panoramic;",
    'window': "SELECT window({col}, 5) FROM sve_exp_operator_panoramic;",

    # --- xpath 系列函数 ---
    'xpath': "SELECT xpath({col}, '//a') FROM sve_exp_operator_panoramic;",
    'xpath_boolean': "SELECT xpath_boolean({col}, '//a') FROM sve_exp_operator_panoramic;",
    'xpath_double': "SELECT xpath_double({col}, '//a') FROM sve_exp_operator_panoramic;",
    'xpath_float': "SELECT xpath_float({col}, '//a') FROM sve_exp_operator_panoramic;",
    'xpath_int': "SELECT xpath_int({col}, '//a') FROM sve_exp_operator_panoramic;",
    'xpath_long': "SELECT xpath_long({col}, '//a') FROM sve_exp_operator_panoramic;",
    'xpath_number': "SELECT xpath_number({col}, '//a') FROM sve_exp_operator_panoramic;",
    'xpath_short': "SELECT xpath_short({col}, '//a') FROM sve_exp_operator_panoramic;",
    'xpath_string': "SELECT xpath_string({col}, '//a') FROM sve_exp_operator_panoramic;",

    # --- 特殊SQL语法的函数 ---
    'aggregate': "SELECT aggregate({col}, 0, (acc, x) -> acc + x, acc -> acc * 2) FROM sve_exp_operator_panoramic;",
    'approx_percentile': "SELECT approx_percentile({col}, 0.5, 10000) FROM sve_exp_operator_panoramic;",
    'case': "SELECT CASE WHEN c_bool THEN {col} ELSE {col} END FROM sve_exp_operator_panoramic;",
    'coalesce': "SELECT coalesce({col}, {col}, {col}) FROM sve_exp_operator_panoramic;",
    'conv': "SELECT conv({col}, 10, 2) FROM sve_exp_operator_panoramic;",
    'count_min_sketch': "SELECT count_min_sketch({col}, 0.01, 0.5, 1) FROM sve_exp_operator_panoramic;",
    'exists': "SELECT exists({col}, x -> x > 0) FROM sve_exp_operator_panoramic;",
    'extract': "SELECT extract(day FROM {col}) FROM sve_exp_operator_panoramic;",
    'filter': "SELECT filter({col}, x -> x > 0) FROM sve_exp_operator_panoramic;",
    'forall': "SELECT forall({col}, x -> x > 0) FROM sve_exp_operator_panoramic;",
    'from_json': "SELECT from_json(c_string, 'a INT') FROM sve_exp_operator_panoramic;",
    'greatest': "SELECT greatest({col}, {col}, {col}) FROM sve_exp_operator_panoramic;",
    'if': "SELECT if(c_bool, {col}, {col}) FROM sve_exp_operator_panoramic;",
    'ilike': "SELECT {col} ILIKE 'pattern' FROM sve_exp_operator_panoramic;",
    'least': "SELECT least({col}, {col}, {col}) FROM sve_exp_operator_panoramic;",
    'like': "SELECT {col} LIKE 'pattern' FROM sve_exp_operator_panoramic;",
    'map_filter': "SELECT map_filter({col}, (k, v) -> v > 0) FROM sve_exp_operator_panoramic;",
    'map_zip_with': "SELECT map_zip_with({col}, {col}, (k, v1, v2) -> v1 + v2) FROM sve_exp_operator_panoramic;",
    'nth_value': "SELECT nth_value({col}, 1) OVER (ORDER BY c_int) FROM sve_exp_operator_panoramic;",
    'overlay': "SELECT overlay({col} PLACING 'test' FROM 1 FOR 4) FROM sve_exp_operator_panoramic;",
    'position': "SELECT position('sub' IN {col}) FROM sve_exp_operator_panoramic;",
    'regexp_extract': "SELECT regexp_extract({col}, 'pattern', 1) FROM sve_exp_operator_panoramic;",
    'regexp_replace': "SELECT regexp_replace({col}, 'pattern', 1) FROM sve_exp_operator_panoramic;",
    'regexp_substr': "SELECT regexp_substr({col}, 'pattern', 1) FROM sve_exp_operator_panoramic;",
    'replace': "SELECT replace({col}, 'old', 'new') FROM sve_exp_operator_panoramic;",
    'substring_index': "SELECT substring_index({col}, ',', 1) FROM sve_exp_operator_panoramic;",
    'transform': "SELECT transform({col}, x -> x * 2) FROM sve_exp_operator_panoramic;",
    'transform_keys': "SELECT transform_keys({col}, (k, v) -> k * 2) FROM sve_exp_operator_panoramic;",
    'transform_values': "SELECT transform_values({col}, (k, v) -> v * 2) FROM sve_exp_operator_panoramic;",
    'translate': "SELECT translate({col}, 'abc', 'xyz') FROM sve_exp_operator_panoramic;",
    'when': "SELECT CASE WHEN {col} > 0 THEN {col} ELSE {col} END FROM sve_exp_operator_panoramic;",
    'width_bucket': "SELECT width_bucket({col}, 0, 100, 10) FROM sve_exp_operator_panoramic;",
    'zip_with': "SELECT zip_with({col}, {col}, (x, y) -> x + y) FROM sve_exp_operator_panoramic;",
    'nvl2': "SELECT nvl2(c_bool, {col}, {col}) FROM sve_exp_operator_panoramic;",
    'rlike': "SELECT {col} RLIKE 'pattern' FROM sve_exp_operator_panoramic;",
    'regexp': "SELECT {col} REGEXP 'pattern' FROM sve_exp_operator_panoramic;",
}

# 二元运算符
BINARY_OPERATORS = frozenset([
    '-', '+', '*', '/', '%', '&', '|', '^', '||',
    '=', '==', '!=', '<>', '<', '<=', '>', '>=', '<=>',
    'and', 'or',
])

# 一元运算符
UNARY_OPERATORS = {
    '!': 'SELECT !{col} FROM sve_exp_operator_panoramic;',
    '~': 'SELECT ~{col} FROM sve_exp_operator_panoramic;',
    '-': 'SELECT -{col} FROM sve_exp_operator_panoramic;',
}

# 特殊运算符
SPECIAL_OPERATORS = {
    'between': 'SELECT {col} BETWEEN {col} AND {col} FROM sve_exp_operator_panoramic;',
    'in': 'SELECT {col} IN ({col}, {col}) FROM sve_exp_operator_panoramic;',
    'not': 'SELECT NOT {col} FROM sve_exp_operator_panoramic;',
}

# ============================================================
# 白名单：函数类型支持规则
# 每个函数映射到其支持的数据类型集合
# 不在映射中的函数默认生成所有类型
# ============================================================

# 类型分组
_NUMERIC = frozenset({'BYTE', 'SHORT', 'INT', 'LONG', 'FLOAT', 'DOUBLE', 'DECIMAL64', 'DECIMAL128'})
_STRING = frozenset({'STRING', 'CHAR', 'VARCHAR'})
_DATETIME = frozenset({'DATE', 'TIMESTAMP'})
_ALL = frozenset(TYPE_COLUMNS)
_BOOL = frozenset({'BOOLEAN'})
_COLLECTION = frozenset({'ARRAY', 'MAP', 'STRUCT(ROW)'})
_ARRAY = frozenset({'ARRAY'})
_MAP = frozenset({'MAP'})
_BINARY = frozenset({'BINARY'})
_SORTABLE = frozenset({'BYTE', 'SHORT', 'INT', 'LONG', 'FLOAT', 'DOUBLE', 'DECIMAL64', 'DECIMAL128',
                       'STRING', 'CHAR', 'VARCHAR', 'DATE', 'TIMESTAMP'})

# 按函数类别批量构建 supported types 映射
FUNC_SUPPORTED_TYPES = {}

# 数值函数
for _f in ['abs', 'acos', 'asin', 'atan', 'atan2', 'cbrt', 'cos', 'cosh', 'degrees', 'exp',
           'hypot', 'ln', 'log', 'log10', 'log2', 'negative', 'positive', 'pow', 'power',
           'radians', 'sign', 'signum', 'sin', 'sinh', 'sqrt', 'tan', 'tanh',
           'ceil', 'ceiling', 'floor', 'round', 'bround', 'div', 'mod', 'pmod',
           'shiftleft', 'shiftright', 'shiftrightunsigned', 'bit_get', 'getbit',
           'width_bucket', 'pmod']:
    FUNC_SUPPORTED_TYPES[_f] = _NUMERIC

# 聚合函数（数值型）
for _f in ['avg', 'sum', 'stddev', 'stddev_pop', 'stddev_samp', 'variance', 'var_pop', 'var_samp',
           'kurtosis', 'skewness', 'corr', 'covar_pop', 'covar_samp', 'histogram_numeric',
           'percentile', 'percentile_approx', 'approx_percentile', 'regr_count', 'regr_r2']:
    FUNC_SUPPORTED_TYPES[_f] = _NUMERIC

# 聚合函数（所有类型）
for _f in ['count', 'max', 'min', 'max_by', 'min_by', 'collect_list', 'collect_set']:
    FUNC_SUPPORTED_TYPES[_f] = _ALL

# 字符串函数
for _f in ['upper', 'lower', 'lcase', 'ucase', 'trim', 'ltrim', 'rtrim', 'btrim',
           'initcap', 'reverse', 'length', 'len', 'char_length', 'character_length',
           'lpad', 'rpad', 'left', 'right', 'substr', 'substring', 'substring_index',
           'concat', 'replace', 'translate', 'instr', 'locate', 'position',
           'split', 'split_part', 'repeat', 'levenshtein',
           'contains', 'startswith', 'endswith', 'like', 'ilike', 'rlike', 'regexp', 'regexp_like',
           'regexp_extract', 'regexp_replace', 'regexp_substr', 'regexp_extract_all',
           'find_in_set', 'overlay', 'printf', 'octet_length', 'bit_length']:
    FUNC_SUPPORTED_TYPES[_f] = _STRING

# 日期/时间函数
for _f in ['day', 'dayofmonth', 'dayofweek', 'dayofyear', 'hour', 'minute', 'second',
           'month', 'quarter', 'year', 'weekday', 'weekofyear', 'last_day',
           'next_day', 'months_between', 'add_months', 'date_add', 'date_sub',
           'datediff', 'date_diff', 'date_trunc', 'date_part', 'trunc',
           'to_date', 'to_timestamp', 'try_to_date', 'try_to_timestamp',
           'from_utc_timestamp', 'to_utc_timestamp', 'unix_date', 'unix_seconds',
           'unix_millis', 'unix_micros', 'extract', 'session_window', 'window']:
    FUNC_SUPPORTED_TYPES[_f] = _DATETIME

# 无参数函数（所有类型生成相同SQL）
for _f in ['pi', 'e', 'rand', 'randn', 'random', 'uuid', 'version',
           'current_date', 'current_timestamp', 'localtimestamp', 'now',
           'spark_partition_id', 'current_catalog', 'current_database', 'current_timezone',
           'input_file_block_length', 'input_file_block_start', 'input_file_name',
           'monotonically_increasing_id', 'make_date', 'make_timestamp']:
    FUNC_SUPPORTED_TYPES[_f] = _ALL

# 窗口函数（无参数，所有类型相同SQL）
for _f in ['row_number', 'rank', 'dense_rank', 'percent_rank', 'cume_dist', 'ntile']:
    FUNC_SUPPORTED_TYPES[_f] = _ALL

# 数组函数
for _f in ['array_distinct', 'array_max', 'array_min', 'array_sort', 'sort_array',
           'array_length', 'array_size', 'size', 'cardinality', 'flatten',
           'array_contains', 'array_except', 'array_intersect', 'array_join',
           'array_position', 'array_remove', 'array_repeat', 'array_union', 'arrays_overlap',
           'slice', 'exists', 'filter', 'forall', 'transform', 'aggregate',
           'array_compact', 'array_prepend', 'array_append', 'array_insert']:
    FUNC_SUPPORTED_TYPES[_f] = _ARRAY

# Map函数
for _f in ['map_keys', 'map_values', 'map_contains_key', 'map_from_arrays',
           'map_filter', 'map_zip_with', 'transform_keys', 'transform_values']:
    FUNC_SUPPORTED_TYPES[_f] = _MAP

# 哈希/编码函数（STRING + BINARY）
for _f in ['md5', 'sha', 'sha1', 'sha2', 'crc32', 'base64', 'unbase64',
           'encode', 'bin', 'hex', 'unhex']:
    FUNC_SUPPORTED_TYPES[_f] = frozenset({'STRING', 'CHAR', 'VARCHAR', 'BINARY'})

# hash 函数支持大多数类型
FUNC_SUPPORTED_TYPES['hash'] = frozenset({'STRING', 'CHAR', 'VARCHAR', 'BINARY',
                                           'BYTE', 'SHORT', 'INT', 'LONG',
                                           'FLOAT', 'DOUBLE', 'DECIMAL64', 'DECIMAL128',
                                           'DATE', 'TIMESTAMP', 'BOOLEAN', 'NULL'})
FUNC_SUPPORTED_TYPES['xxhash64'] = FUNC_SUPPORTED_TYPES['hash']

# 类型检查函数
for _f in ['isnull', 'isnotnull']:
    FUNC_SUPPORTED_TYPES[_f] = _ALL
FUNC_SUPPORTED_TYPES['isnan'] = _NUMERIC  # NaN只存在于数值类型

# 通用函数（所有类型）
for _f in ['coalesce', 'nvl', 'nvl2', 'nullif', 'ifnull', 'nanvl',
           'greatest', 'least', 'case', 'when', 'if']:
    FUNC_SUPPORTED_TYPES[_f] = _ALL

# 布尔函数
for _f in ['!']:
    FUNC_SUPPORTED_TYPES[_f] = frozenset({'BOOLEAN'})

# 二元运算符（可排序类型）
for _f in ['=', '==', '!=', '<>', '<', '<=', '>', '>=', '<=>']:
    FUNC_SUPPORTED_TYPES[_f] = _SORTABLE

# 算术运算符
for _f in ['+', '-', '*', '/', '%', '&', '|', '^']:
    FUNC_SUPPORTED_TYPES[_f] = _NUMERIC

# 字符串连接
FUNC_SUPPORTED_TYPES['||'] = _STRING

# 逻辑运算符
for _f in ['and', 'or']:
    FUNC_SUPPORTED_TYPES[_f] = _BOOL

# 位运算符
FUNC_SUPPORTED_TYPES['~'] = _NUMERIC

# 特殊运算符
FUNC_SUPPORTED_TYPES['between'] = _SORTABLE
FUNC_SUPPORTED_TYPES['in'] = _SORTABLE
FUNC_SUPPORTED_TYPES['not'] = _BOOL

# XPath函数（STRING输入）
for _f in ['xpath', 'xpath_boolean', 'xpath_double', 'xpath_float', 'xpath_int',
           'xpath_long', 'xpath_number', 'xpath_short', 'xpath_string']:
    FUNC_SUPPORTED_TYPES[_f] = _STRING

# 其他特殊函数
FUNC_SUPPORTED_TYPES['from_json'] = _STRING
FUNC_SUPPORTED_TYPES['from_csv'] = _STRING
FUNC_SUPPORTED_TYPES['element_at'] = frozenset({'ARRAY', 'MAP'})
FUNC_SUPPORTED_TYPES['try_element_at'] = frozenset({'ARRAY', 'MAP'})
FUNC_SUPPORTED_TYPES['sequence'] = _NUMERIC
FUNC_SUPPORTED_TYPES['conv'] = _NUMERIC
FUNC_SUPPORTED_TYPES['count_min_sketch'] = _NUMERIC
FUNC_SUPPORTED_TYPES['format_number'] = _NUMERIC
FUNC_SUPPORTED_TYPES['to_number'] = _STRING
FUNC_SUPPORTED_TYPES['try_to_number'] = _STRING
FUNC_SUPPORTED_TYPES['try_add'] = _NUMERIC
FUNC_SUPPORTED_TYPES['try_divide'] = _NUMERIC
FUNC_SUPPORTED_TYPES['try_multiply'] = _NUMERIC
FUNC_SUPPORTED_TYPES['try_subtract'] = _NUMERIC
FUNC_SUPPORTED_TYPES['zip_with'] = _ARRAY
FUNC_SUPPORTED_TYPES['nth_value'] = _ALL
FUNC_SUPPORTED_TYPES['first_value'] = _ALL
FUNC_SUPPORTED_TYPES['last_value'] = _ALL
FUNC_SUPPORTED_TYPES['lag'] = _ALL
FUNC_SUPPORTED_TYPES['lead'] = _ALL
FUNC_SUPPORTED_TYPES['aes_decrypt'] = _BINARY
FUNC_SUPPORTED_TYPES['aes_encrypt'] = _BINARY
FUNC_SUPPORTED_TYPES['any_value'] = _ALL

# 不支持时的输出标记
UNSUPPORTED_MARKER = 'ns'


def get_supported_types(func_name):
    """返回函数支持的数据类型集合，未知函数返回None（表示生成所有类型）"""
    return FUNC_SUPPORTED_TYPES.get(func_name)


def generate_function_sql(func_name, dtype, col, func_type, description):
    """
    根据函数名、数据类型和列名生成SQL语句
    优先查字典，匹配不到再按运算符和参数推断处理
    """
    # 1. 字典精确匹配
    if func_name in FUNC_SQL_TEMPLATES:
        return FUNC_SQL_TEMPLATES[func_name].replace('{col}', col)

    # 2. 二元运算符
    if func_name in BINARY_OPERATORS:
        return f'SELECT {col} {func_name} {col} FROM sve_exp_operator_panoramic;'

    # 3. 一元运算符
    if func_name in UNARY_OPERATORS:
        return UNARY_OPERATORS[func_name].replace('{col}', col)

    # 4. 特殊运算符
    if func_name in SPECIAL_OPERATORS:
        return SPECIAL_OPERATORS[func_name].replace('{col}', col)

    # 5. 未知函数：从描述推断参数数量，生成默认SQL
    func_type_lower = (func_type or '').lower()
    is_window = 'window' in func_type_lower

    param_count = 1
    desc = description or ''
    sig_match = re.search(r'(\w+)\s*\(([^)]+)\)', desc)
    if sig_match:
        params = [p.strip() for p in sig_match.group(2).split(',')]
        param_count = len([p for p in params if not p.startswith('[')])

    if is_window:
        return f'SELECT {func_name}({col}) OVER (ORDER BY c_int) FROM sve_exp_operator_panoramic;'

    if param_count <= 1:
        return f'SELECT {func_name}({col}) FROM sve_exp_operator_panoramic;'
    elif param_count == 2:
        return f'SELECT {func_name}({col}, {col}) FROM sve_exp_operator_panoramic;'
    elif param_count == 3:
        return f'SELECT {func_name}({col}, {col}, {col}) FROM sve_exp_operator_panoramic;'
    else:
        return f'SELECT {func_name}({col}, {col}, {col}) FROM sve_exp_operator_panoramic;'


def generate_sql_for_function(func_name, func_type, description, velox_status, restrictions, all_types=False):
    """
    根据函数信息生成19种数据类型的测试SQL
    all_types=True 时忽略白名单，对所有类型生成SQL（向后兼容）
    否则根据 FUNC_SUPPORTED_TYPES 过滤，不支持的类型标记为 ns
    """
    supported = None if all_types else get_supported_types(func_name)
    results = {}
    for dtype in TYPE_COLUMNS:
        # 白名单过滤
        if supported is not None and dtype not in supported:
            results[dtype] = UNSUPPORTED_MARKER
            continue

        col = TYPE_TO_COLUMN.get(dtype)
        if col:
            sql = generate_function_sql(func_name, dtype, col, func_type, description)
            results[dtype] = sql if sql else f'无法生成{dtype}类型的SQL'
        else:
            results[dtype] = f'表结构不支持{dtype}类型'
    return results


def process_csv(input_file, output_file, all_types=False):
    """
    处理CSV文件，为所有函数生成测试SQL
    如果状态列已经是"已完成"，则跳过处理

    Args:
        input_file: 输入CSV文件路径
        output_file: 输出CSV文件路径
        all_types: True=对所有类型生成SQL（向后兼容），False=按白名单过滤
    """
    encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']
    rows = None
    for enc in encodings:
        try:
            with open(input_file, 'r', encoding=enc) as f:
                reader = csv.reader(f)
                rows = list(reader)
                if rows and len(rows) > 0:
                    print(f"成功使用编码 {enc} 读取文件，共 {len(rows)} 行")
                    break
        except Exception as e:
            print(f"尝试编码 {enc} 失败: {e}")
            continue

    if rows is None:
        raise ValueError("无法读取CSV文件，尝试了所有编码")

    header = rows[0]

    func_name_idx = header.index('spark表达式(Spark Functions)')
    func_class_idx = header.index('Spark类(Spark Expressions)')
    func_type_idx = header.index('函数类型')
    description_idx = header.index('Spark表达式功能简述')

    try:
        restrictions_idx = header.index('velox支持情况/限制(Restrictions)')
    except ValueError:
        restrictions_idx = None

    try:
        velox_status_idx = header.index('Velox支持性(Status)')
    except ValueError:
        velox_status_idx = None

    try:
        status_idx = header.index('状态')
    except ValueError:
        status_idx = None
        print("警告：未找到'状态'列，将跳过状态检查")

    type_indices = {}
    for dtype in TYPE_COLUMNS:
        if dtype in header:
            type_indices[dtype] = header.index(dtype)
        else:
            print(f"警告：未找到数据类型列 {dtype}")

    processed_count = 0
    skipped_count = 0

    for row_idx in range(1, len(rows)):
        row = rows[row_idx]

        if len(row) <= func_name_idx:
            continue

        func_name = row[func_name_idx].strip().strip('"')

        if not func_name:
            continue

        func_class = row[func_class_idx].strip() if func_class_idx < len(row) else ''
        func_type = row[func_type_idx].strip() if func_type_idx < len(row) else ''
        description = row[description_idx].strip() if description_idx < len(row) else ''
        restrictions = row[restrictions_idx].strip() if restrictions_idx is not None and restrictions_idx < len(row) else ''
        velox_status = row[velox_status_idx].strip() if velox_status_idx is not None and velox_status_idx < len(row) else ''
        current_status = row[status_idx].strip() if status_idx is not None and status_idx < len(row) else ''

        if status_idx is not None and current_status == '已完成':
            print(f"跳过: {func_name} (已完成)")
            skipped_count += 1
            continue

        print(f"处理: {func_name} (第 {row_idx + 1} 行)")

        sql_results = generate_sql_for_function(func_name, func_type, description, velox_status, restrictions, all_types=all_types)

        for dtype, sql in sql_results.items():
            if dtype in type_indices:
                idx = type_indices[dtype]
                while len(row) <= idx:
                    row.append('')
                row[idx] = sql

        if status_idx is not None:
            if len(row) > status_idx:
                row[status_idx] = '已完成'
            else:
                while len(row) <= status_idx:
                    row.append('')
                row[status_idx] = '已完成'

        rows[row_idx] = row
        processed_count += 1

    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerows(rows)

    print(f"\n处理完成！")
    print(f"  处理了 {processed_count} 个函数")
    print(f"  跳过了 {skipped_count} 个已完成函数")
    print(f"  结果已保存到 {output_file}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Spark表达式测试SQL生成')
    parser.add_argument('input_file', help='输入CSV文件路径')
    parser.add_argument('output_file', help='输出CSV文件路径')
    parser.add_argument('--all', action='store_true', dest='all_types',
                        help='对所有数据类型生成SQL（忽略白名单，向后兼容）')
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"错误：输入文件不存在: {args.input_file}")
        sys.exit(1)

    mode = "全类型" if args.all_types else "白名单"
    print(f"运行模式: {mode}")
    process_csv(args.input_file, args.output_file, all_types=args.all_types)
