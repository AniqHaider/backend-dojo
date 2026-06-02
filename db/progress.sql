PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE exercise_progress (
                    exercise_id TEXT PRIMARY KEY,
                    status      TEXT NOT NULL DEFAULT 'unsolved',
                    attempts    INTEGER NOT NULL DEFAULT 0,
                    solved_at   TEXT,
                    best_code   TEXT
                );
INSERT INTO exercise_progress VALUES('ch1-ex01-greeting','solved',1,'2026-06-01T08:07:51.261148+00:00',unistr('def greet(name):\u000a    return f"Hello, {name}!"'));
INSERT INTO exercise_progress VALUES('ch1-ex08-loops','unsolved',13,NULL,unistr('def sum_evens(nums):\u000a    pass\u000a'));
INSERT INTO exercise_progress VALUES('ch1-ex02-types','solved',45,'2026-06-01T16:47:36.998269+00:00',unistr('def to_int(s):\u000a  return int(s)'));
INSERT INTO exercise_progress VALUES('ch1-ex03-arithmetic','solved',10,'2026-06-02T03:36:03.428909+00:00',unistr('def total_price(qty, unit):\u000a    i = qty * unit\u000a    return i\u000a\u000a\u000a# def total_price(qty, unit):\u000a#    return qty * unit\u000a   \u000a'));
INSERT INTO exercise_progress VALUES('ch1-ex04-strings','unsolved',4,NULL,unistr('def initials(full_name):\u000a    for(i=0, i<full_name.length, i++)\u000a        arr = []\u000a        arr.append[full_name[0]]\u000a        if : full_name[i] == '' ''\u000a            arr.append[full_name[i+1]]\u000a\u000a\u000a     return arr\u000a          \u000a        '));
CREATE TABLE mistakes_log (
                    id             INTEGER PRIMARY KEY AUTOINCREMENT,
                    exercise_id    TEXT NOT NULL,
                    ts             TEXT NOT NULL,
                    error_category TEXT,
                    detail         TEXT
                );
INSERT INTO mistakes_log VALUES(1,'ch1-ex08-loops','2026-06-01T09:52:33.276944+00:00','wrong_output','sum_evens([1, 2, 3, 4]) -> expected 6, got None');
INSERT INTO mistakes_log VALUES(2,'ch1-ex08-loops','2026-06-01T09:52:35.335134+00:00','wrong_output','sum_evens([1, 2, 3, 4]) -> expected 6, got None');
INSERT INTO mistakes_log VALUES(3,'ch1-ex08-loops','2026-06-01T09:52:35.916309+00:00','wrong_output','sum_evens([1, 2, 3, 4]) -> expected 6, got None');
INSERT INTO mistakes_log VALUES(4,'ch1-ex08-loops','2026-06-01T09:52:36.350416+00:00','wrong_output','sum_evens([1, 2, 3, 4]) -> expected 6, got None');
INSERT INTO mistakes_log VALUES(5,'ch1-ex08-loops','2026-06-01T09:52:36.582724+00:00','wrong_output','sum_evens([1, 2, 3, 4]) -> expected 6, got None');
INSERT INTO mistakes_log VALUES(6,'ch1-ex08-loops','2026-06-01T09:52:36.735042+00:00','wrong_output','sum_evens([1, 2, 3, 4]) -> expected 6, got None');
INSERT INTO mistakes_log VALUES(7,'ch1-ex08-loops','2026-06-01T09:52:36.949616+00:00','wrong_output','sum_evens([1, 2, 3, 4]) -> expected 6, got None');
INSERT INTO mistakes_log VALUES(8,'ch1-ex08-loops','2026-06-01T09:52:37.063585+00:00','wrong_output','sum_evens([1, 2, 3, 4]) -> expected 6, got None');
INSERT INTO mistakes_log VALUES(9,'ch1-ex08-loops','2026-06-01T09:52:37.368228+00:00','wrong_output','sum_evens([1, 2, 3, 4]) -> expected 6, got None');
INSERT INTO mistakes_log VALUES(10,'ch1-ex08-loops','2026-06-01T09:52:37.517969+00:00','wrong_output','sum_evens([1, 2, 3, 4]) -> expected 6, got None');
INSERT INTO mistakes_log VALUES(11,'ch1-ex08-loops','2026-06-01T09:52:37.750075+00:00','wrong_output','sum_evens([1, 2, 3, 4]) -> expected 6, got None');
INSERT INTO mistakes_log VALUES(12,'ch1-ex08-loops','2026-06-01T09:52:37.945353+00:00','wrong_output','sum_evens([1, 2, 3, 4]) -> expected 6, got None');
INSERT INTO mistakes_log VALUES(13,'ch1-ex08-loops','2026-06-01T09:52:38.123983+00:00','wrong_output','sum_evens([1, 2, 3, 4]) -> expected 6, got None');
INSERT INTO mistakes_log VALUES(14,'ch1-ex02-types','2026-06-01T16:21:39.317876+00:00','syntax_error',unistr('File "/tmp/claude-501/tmpq95ktij4/submission.py", line 2\u000a    pass here\u000a         ^^^^\u000aSyntaxError: invalid syntax'));
INSERT INTO mistakes_log VALUES(15,'ch1-ex03-arithmetic','2026-06-01T16:27:24.476793+00:00','syntax_error',unistr('File "/tmp/claude-501/tmpkgii22sm/submission.py", line 2\u000a    pass total_price(3, 50)\u000a         ^^^^^^^^^^^\u000aSyntaxError: invalid syntax'));
INSERT INTO mistakes_log VALUES(16,'ch1-ex02-types','2026-06-01T16:29:19.007572+00:00','syntax_error',unistr('File "/tmp/claude-501/tmpfozb0o11/submission.py", line 2\u000a    pass toint(''42'')\u000a         ^^^^^\u000aSyntaxError: invalid syntax'));
INSERT INTO mistakes_log VALUES(17,'ch1-ex02-types','2026-06-01T16:29:28.356015+00:00','syntax_error',unistr('File "/tmp/claude-501/tmp_21zfx4w/submission.py", line 2\u000a    pass to_int(''42'')\u000a         ^^^^^^\u000aSyntaxError: invalid syntax'));
INSERT INTO mistakes_log VALUES(18,'ch1-ex02-types','2026-06-01T16:31:22.544697+00:00','syntax_error',unistr('File "/tmp/claude-501/tmpe4_kx8r8/submission.py", line 1\u000a    print int(''-7'') \u000a    ^^^^^^^^^^^^^^^\u000aSyntaxError: Missing parentheses in call to ''print''. Did you mean print(...)?'));
INSERT INTO mistakes_log VALUES(19,'ch1-ex02-types','2026-06-01T16:31:23.373448+00:00','syntax_error',unistr('File "/tmp/claude-501/tmp567avqbv/submission.py", line 1\u000a    print int(''-7'') \u000a    ^^^^^^^^^^^^^^^\u000aSyntaxError: Missing parentheses in call to ''print''. Did you mean print(...)?'));
INSERT INTO mistakes_log VALUES(20,'ch1-ex02-types','2026-06-01T16:31:41.371568+00:00','syntax_error',unistr('File "/tmp/claude-501/tmpw_4q55kv/submission.py", line 1\u000a    print{int(''-7'')}\u000a    ^^^^^^^^^^^^^^^^\u000aSyntaxError: Missing parentheses in call to ''print''. Did you mean print(...)?'));
INSERT INTO mistakes_log VALUES(21,'ch1-ex02-types','2026-06-01T16:31:42.034442+00:00','syntax_error',unistr('File "/tmp/claude-501/tmpx4xvz6lz/submission.py", line 1\u000a    print{int(''-7'')}\u000a    ^^^^^^^^^^^^^^^^\u000aSyntaxError: Missing parentheses in call to ''print''. Did you mean print(...)?'));
INSERT INTO mistakes_log VALUES(22,'ch1-ex02-types','2026-06-01T16:31:43.239301+00:00','syntax_error',unistr('File "/tmp/claude-501/tmph6j7t_b1/submission.py", line 1\u000a    print{int(''-7'')}\u000a    ^^^^^^^^^^^^^^^^\u000aSyntaxError: Missing parentheses in call to ''print''. Did you mean print(...)?'));
INSERT INTO mistakes_log VALUES(23,'ch1-ex02-types','2026-06-01T16:31:44.390531+00:00','syntax_error',unistr('File "/tmp/claude-501/tmpj09jay76/submission.py", line 1\u000a    print{int(''-7'')}\u000a    ^^^^^^^^^^^^^^^^\u000aSyntaxError: Missing parentheses in call to ''print''. Did you mean print(...)?'));
INSERT INTO mistakes_log VALUES(24,'ch1-ex02-types','2026-06-01T16:35:09.309428+00:00','syntax_error',unistr('File "/tmp/claude-501/tmptc1hslsw/submission.py", line 1\u000a    print to_int(s);\u000a    ^^^^^^^^^^^^^^^\u000aSyntaxError: Missing parentheses in call to ''print''. Did you mean print(...)?'));
INSERT INTO mistakes_log VALUES(25,'ch1-ex02-types','2026-06-01T16:35:20.322141+00:00','syntax_error',unistr('File "/tmp/claude-501/tmp3_k9_wyf/submission.py", line 1\u000a    print to_int(s);\u000a    ^^^^^^^^^^^^^^^\u000aSyntaxError: Missing parentheses in call to ''print''. Did you mean print(...)?'));
INSERT INTO mistakes_log VALUES(26,'ch1-ex02-types','2026-06-01T16:35:20.824210+00:00','syntax_error',unistr('File "/tmp/claude-501/tmp860utnk6/submission.py", line 1\u000a    print to_int(s);\u000a    ^^^^^^^^^^^^^^^\u000aSyntaxError: Missing parentheses in call to ''print''. Did you mean print(...)?'));
INSERT INTO mistakes_log VALUES(27,'ch1-ex02-types','2026-06-01T16:35:21.003912+00:00','syntax_error',unistr('File "/tmp/claude-501/tmphtnbzlzs/submission.py", line 1\u000a    print to_int(s);\u000a    ^^^^^^^^^^^^^^^\u000aSyntaxError: Missing parentheses in call to ''print''. Did you mean print(...)?'));
INSERT INTO mistakes_log VALUES(28,'ch1-ex02-types','2026-06-01T16:35:21.205039+00:00','syntax_error',unistr('File "/tmp/claude-501/tmpvnc8s3ot/submission.py", line 1\u000a    print to_int(s);\u000a    ^^^^^^^^^^^^^^^\u000aSyntaxError: Missing parentheses in call to ''print''. Did you mean print(...)?'));
INSERT INTO mistakes_log VALUES(29,'ch1-ex02-types','2026-06-01T16:35:53.570829+00:00','syntax_error',unistr('File "/tmp/claude-501/tmpp7j9385f/submission.py", line 1\u000a    print to_int(''42'')\u000a    ^^^^^^^^^^^^^^^^^^\u000aSyntaxError: Missing parentheses in call to ''print''. Did you mean print(...)?'));
INSERT INTO mistakes_log VALUES(30,'ch1-ex02-types','2026-06-01T16:35:54.185854+00:00','syntax_error',unistr('File "/tmp/claude-501/tmpez2ybqt6/submission.py", line 1\u000a    print to_int(''42'')\u000a    ^^^^^^^^^^^^^^^^^^\u000aSyntaxError: Missing parentheses in call to ''print''. Did you mean print(...)?'));
INSERT INTO mistakes_log VALUES(31,'ch1-ex02-types','2026-06-01T16:35:54.457449+00:00','syntax_error',unistr('File "/tmp/claude-501/tmpo43lne9k/submission.py", line 1\u000a    print to_int(''42'')\u000a    ^^^^^^^^^^^^^^^^^^\u000aSyntaxError: Missing parentheses in call to ''print''. Did you mean print(...)?'));
INSERT INTO mistakes_log VALUES(32,'ch1-ex02-types','2026-06-01T16:35:54.654947+00:00','syntax_error',unistr('File "/tmp/claude-501/tmp009u_t39/submission.py", line 1\u000a    print to_int(''42'')\u000a    ^^^^^^^^^^^^^^^^^^\u000aSyntaxError: Missing parentheses in call to ''print''. Did you mean print(...)?'));
INSERT INTO mistakes_log VALUES(33,'ch1-ex02-types','2026-06-01T16:35:54.837391+00:00','syntax_error',unistr('File "/tmp/claude-501/tmpegddw0yz/submission.py", line 1\u000a    print to_int(''42'')\u000a    ^^^^^^^^^^^^^^^^^^\u000aSyntaxError: Missing parentheses in call to ''print''. Did you mean print(...)?'));
INSERT INTO mistakes_log VALUES(34,'ch1-ex02-types','2026-06-01T16:35:54.990126+00:00','syntax_error',unistr('File "/tmp/claude-501/tmptiicr7u7/submission.py", line 1\u000a    print to_int(''42'')\u000a    ^^^^^^^^^^^^^^^^^^\u000aSyntaxError: Missing parentheses in call to ''print''. Did you mean print(...)?'));
INSERT INTO mistakes_log VALUES(35,'ch1-ex02-types','2026-06-01T16:35:55.188447+00:00','syntax_error',unistr('File "/tmp/claude-501/tmp5q7cvpea/submission.py", line 1\u000a    print to_int(''42'')\u000a    ^^^^^^^^^^^^^^^^^^\u000aSyntaxError: Missing parentheses in call to ''print''. Did you mean print(...)?'));
INSERT INTO mistakes_log VALUES(36,'ch1-ex02-types','2026-06-01T16:36:06.339201+00:00','syntax_error',unistr('File "/tmp/claude-501/tmppx4kbbv9/submission.py", line 1\u000a    print to_int(s);\u000a    ^^^^^^^^^^^^^^^\u000aSyntaxError: Missing parentheses in call to ''print''. Did you mean print(...)?'));
INSERT INTO mistakes_log VALUES(37,'ch1-ex02-types','2026-06-01T16:38:28.990051+00:00','syntax_error',unistr('File "/tmp/claude-501/tmp4ldqkdkq/submission.py", line 1\u000a    def intt()\u000a              ^\u000aSyntaxError: expected '':'''));
INSERT INTO mistakes_log VALUES(38,'ch1-ex02-types','2026-06-01T16:38:29.738088+00:00','syntax_error',unistr('File "/tmp/claude-501/tmpj0nq66yo/submission.py", line 1\u000a    def intt()\u000a              ^\u000aSyntaxError: expected '':'''));
INSERT INTO mistakes_log VALUES(39,'ch1-ex02-types','2026-06-01T16:40:15.454073+00:00','runtime_error','NameError: name ''to_int'' is not defined');
INSERT INTO mistakes_log VALUES(40,'ch1-ex02-types','2026-06-01T16:40:39.086003+00:00','runtime_error','TypeError: to_int() takes 0 positional arguments but 1 was given');
INSERT INTO mistakes_log VALUES(41,'ch1-ex02-types','2026-06-01T16:40:47.436702+00:00','runtime_error','RecursionError: maximum recursion depth exceeded');
INSERT INTO mistakes_log VALUES(42,'ch1-ex02-types','2026-06-01T16:40:55.337182+00:00','runtime_error','RecursionError: maximum recursion depth exceeded');
INSERT INTO mistakes_log VALUES(43,'ch1-ex02-types','2026-06-01T16:41:53.300027+00:00','runtime_error','RecursionError: maximum recursion depth exceeded');
INSERT INTO mistakes_log VALUES(44,'ch1-ex02-types','2026-06-01T16:41:54.103557+00:00','runtime_error','RecursionError: maximum recursion depth exceeded');
INSERT INTO mistakes_log VALUES(45,'ch1-ex02-types','2026-06-01T16:43:48.919811+00:00','runtime_error',unistr('File "/tmp/claude-501/tmpupafkpbr/submission.py", line 3\u000a    return s;\u000aIndentationError: unexpected indent'));
INSERT INTO mistakes_log VALUES(46,'ch1-ex02-types','2026-06-01T16:43:55.092953+00:00','wrong_output','to_int(''42'') -> expected 42, got ''42''');
INSERT INTO mistakes_log VALUES(47,'ch1-ex02-types','2026-06-01T16:44:29.870374+00:00','runtime_error','ValueError: invalid literal for int() with base 10: ''s''');
INSERT INTO mistakes_log VALUES(48,'ch1-ex02-types','2026-06-01T16:44:31.652371+00:00','runtime_error','ValueError: invalid literal for int() with base 10: ''s''');
INSERT INTO mistakes_log VALUES(49,'ch1-ex02-types','2026-06-01T16:44:36.820782+00:00','wrong_output','to_int(''42'') -> expected 42, got ''42''');
INSERT INTO mistakes_log VALUES(50,'ch1-ex02-types','2026-06-01T16:45:10.102630+00:00','wrong_output','to_int(''42'') -> expected 42, got ''42''');
INSERT INTO mistakes_log VALUES(51,'ch1-ex02-types','2026-06-01T16:53:45.710917+00:00','syntax_error',unistr('File "/tmp/claude-501/tmpn2b14o_4/submission.py", line 2\u000a    return i = int(s)\u000a             ^\u000aSyntaxError: invalid syntax'));
INSERT INTO mistakes_log VALUES(52,'ch1-ex02-types','2026-06-01T16:54:49.036942+00:00','runtime_error','NameError: name ''idnt'' is not defined');
INSERT INTO mistakes_log VALUES(53,'ch1-ex03-arithmetic','2026-06-02T03:34:57.432788+00:00','syntax_error',unistr('File "/tmp/claude-501/tmprpcojfj1/submission.py", line 2\u000a    pass total_price(3 * 50)\u000a         ^^^^^^^^^^^\u000aSyntaxError: invalid syntax'));
INSERT INTO mistakes_log VALUES(54,'ch1-ex03-arithmetic','2026-06-02T03:35:05.688400+00:00','runtime_error','TypeError: total_price() missing 1 required positional argument: ''unit''');
INSERT INTO mistakes_log VALUES(55,'ch1-ex03-arithmetic','2026-06-02T03:35:21.228188+00:00','runtime_error','RecursionError: maximum recursion depth exceeded');
INSERT INTO mistakes_log VALUES(56,'ch1-ex03-arithmetic','2026-06-02T03:38:02.043917+00:00','runtime_error',unistr('File "/tmp/claude-501/tmp3g2m1uax/submission.py", line 3\u000a    return i\u000aIndentationError: unexpected indent'));
INSERT INTO mistakes_log VALUES(57,'ch1-ex04-strings','2026-06-02T03:46:58.959701+00:00','syntax_error',unistr('File "/tmp/claude-501/tmpfv6a4gz2/submission.py", line 2\u000a    for(i=0, i<full_name.length, i++)\u000a        ^^^\u000aSyntaxError: invalid syntax. Maybe you meant ''=='' or '':='' instead of ''=''?'));
INSERT INTO mistakes_log VALUES(58,'ch1-ex04-strings','2026-06-02T03:47:18.461904+00:00','syntax_error',unistr('File "/tmp/claude-501/tmpplrr9dh5/submission.py", line 2\u000a    for(i:=0, i<full_name.length, i++)\u000a                                     ^\u000aSyntaxError: invalid syntax'));
INSERT INTO mistakes_log VALUES(59,'ch1-ex04-strings','2026-06-02T03:47:26.597413+00:00','syntax_error',unistr('File "/tmp/claude-501/tmpl7w35ssv/submission.py", line 2\u000a    for(i=0, i<full_name.length, i++)\u000a        ^^^\u000aSyntaxError: invalid syntax. Maybe you meant ''=='' or '':='' instead of ''=''?'));
INSERT INTO mistakes_log VALUES(60,'ch1-ex04-strings','2026-06-02T03:52:27.031786+00:00','syntax_error',unistr('File "/tmp/claude-501/tmplkzyer21/submission.py", line 2\u000a    for(i=0, i<full_name.length, i++)\u000a        ^^^\u000aSyntaxError: invalid syntax. Maybe you meant ''=='' or '':='' instead of ''=''?'));
CREATE TABLE stats (
                    id              INTEGER PRIMARY KEY CHECK (id = 1),
                    xp              INTEGER NOT NULL DEFAULT 0,
                    level           INTEGER NOT NULL DEFAULT 1,
                    current_streak  INTEGER NOT NULL DEFAULT 0,
                    longest_streak  INTEGER NOT NULL DEFAULT 0,
                    last_active_date TEXT
                );
INSERT INTO stats VALUES(1,30,1,2,2,'2026-06-02');
CREATE TABLE diagram_state (
                    component_id TEXT PRIMARY KEY,
                    unlocked     INTEGER NOT NULL DEFAULT 0,
                    unlocked_at  TEXT
                );
INSERT INTO diagram_state VALUES('py-runtime',1,'2026-06-01T08:07:51.266656+00:00');
INSERT INTO sqlite_sequence VALUES('mistakes_log',60);
COMMIT;
