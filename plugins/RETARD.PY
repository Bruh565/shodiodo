import redis

r_db = redis.Redis(port=port, db=db)

def limit_request(request_to_make, limit=3, per=1, request_name='test', **kwargs):
    over_limit_lua_ = '''
    local key_name = KEYS[1]
    local limit = tonumber(ARGV[1])
    local duration = ARGV[2]

    local key = key_name .. '_num_of_requests'
    local count = redis.call('INCR', key)
    if tonumber(count) > limit then
        local time_left = redis.call('PTTL', key)
        return time_left
    end
    redis.call('EXPIRE', key, duration)
    return -2
    '''

    if not hasattr(r_db, 'over_limit_lua'):
        r_db.over_limit_lua = r_db.register_script(over_limit_lua_)

    request_possibility = int(r_db.over_limit_lua(keys=request_name, args=[limit, per]))
    if request_possibility > 0:
        time.sleep(request_possibility / 1000.0)
        return limit_request(request_to_make, limit, per, request_name, **kwargs)
    else:
        request_result = request_to_make(**kwargs)
        return request_result
