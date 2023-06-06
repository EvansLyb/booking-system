from datetime import date, timedelta

"""
For Lock Info
input: ["01:30-03:20", "10:05-13:31", "06:56-07:59", "17:30-24:00", "13:12-19:20", "18:20-23:00"]
output: ["01:30-03:20", "06:56-07:59", "10:05-24:00"]
"""
def merge_time_list(time_slot_list):
    merge_time_set = set()
    time_slot_list.sort()
    cur_start, cur_end = split_time(time_slot_list[0])
    for time_slot in time_slot_list[1:]:
        next_start, next_end = split_time(time_slot)
        if next_start > cur_end:
            merge_time_set.add(f'{cur_start}-{cur_end}')
            cur_start = next_start
            cur_end = next_end
            continue
        if next_start <= cur_end:
            cur_end = max(cur_end, next_end)
            continue
    merge_time_set.add(f'{cur_start}-{cur_end}')
    merge_time_list = list(merge_time_set)
    merge_time_list.sort()
    return merge_time_list


"""
For Lock Info
input1: ["01:30-03:30"], "02:00-02:30"
output1: ["01:30-02:00", "02:30-03:30"]
input2: ["01:30-03:30"], "01:00-02:30"
output2: ["02:30-03:30"]
input3: ["01:30-03:30"], "02:30-05:30"
output3: ["01:30-02:30"]
input4: ["01:30-03:30"], "01:30-03:30"
output4: []
input5: ["01:30-03:30", "06:00-08:00"], "01:00-07:00"
output5: ["07:00-08:00"]
input6: ["01:30-03:30", "06:00-08:00"], "02:00-07:00"
output6: ["01:30-02:00", "06:00-07:00"]
input7: ["01:30-03:30", "06:00-08:00"], "03:00-09:00"
output7: ["01:30-03:00"]
input8: ["01:30-03:30", "06:00-08:00"], "01:00-09:00"
output8: []
"""
def split_time_list(time_slot_list, unlock_time_slot):
    time_set = set()
    is_all_unlocked = False
    time_slot_list.sort()
    start_unlock_time, end_unlock_time = split_time(unlock_time_slot)
    for time_slot in time_slot_list:
        cur_start, cur_end = split_time(time_slot)
        if is_all_unlocked:
            time_set.add(f'{cur_start}-{cur_end}')
            continue
        if start_unlock_time <= cur_start:
            if end_unlock_time < cur_end:
                time_set.add(f'{end_unlock_time}-{cur_end}')
                is_all_unlocked = True
        else:
            if start_unlock_time < cur_end:
                time_set.add(f'{cur_start}-{start_unlock_time}')
            else:
                time_set.add(f'{cur_start}-{cur_end}')
                continue
            if end_unlock_time < cur_end:
                time_set.add(f'{end_unlock_time}-{cur_end}')
                is_all_unlocked = True
            elif end_unlock_time == cur_end:
                is_all_unlocked = True
            else:
                pass
    split_time_list = list(time_set)
    split_time_list.sort()
    return split_time_list


def split_time(time):
    return tuple(time.split('-'))


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


# if __name__ == '__main__':
#     print(split_time_list(["00:30-01:30", "04:30-18:00"], "02:30-07:00"))