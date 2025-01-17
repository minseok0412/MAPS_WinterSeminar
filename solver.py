from module import *
import numpy as np
import random
import pandas as pd

def rule_solver(instance: Prob_Instance, seed):
    # print('Solver Start')
    solution = {}
    solution["Problem"] = instance.deepcopy()
    total_CompletionTime = 0
    sch_list = []

    job_list = instance.job_list
    job: Job
    for job in job_list:
        job.initialize()

    mach_list = instance.machine_list
    mach: Machine
    mach_set = []
    for mach in mach_list:
        mach.initialize()

    setup_matrix = instance.setup_metrix

    for mach in mach_list:
        mach.set_time_matrix = setup_matrix
        mach_set.append(mach.setup_status)

    # solver
    instance, mach_list, job_list, sch_list = match(instance, job_list, mach_list, seed, sch_list)

    for job in job_list:
        total_CompletionTime += job.end_time

    instance.chromo.objective = total_CompletionTime
    solution['Objective'] = []
    solution['Objective'].append(total_CompletionTime)

    return solution, instance.chromo, mach_list, sch_list


def match(instance, job_list, mach_list, seed, sch_list):
    random.seed(seed)
    gene_id = 1
    sch_columns = ['start_time', 'end_time', 'machine_ID', 'job_ID', 'setup_status', 'setup_time','dicision_point']
    df = pd.DataFrame(columns=sch_columns)
    while any(job.done is False for job in job_list):
        not_completed_jobs = list(filter(lambda x: x.done is False, job_list))
        for job in not_completed_jobs:
            avail_mach_list = list(filter(lambda x: x.work_speed_list[job.id - 1] != 0, mach_list))
            avail_mach_list.sort(key=lambda x: x.avail_time)
            dicision_point = avail_mach_list[0].avail_time
            mach = random.choice(mach_list)
            cur = job
            sch_list = []
            setup_time = mach.get_setup_time(previousJob=mach.setup_status, currentJob=cur)
            if mach.work_speed_list[job.id - 1] != 0:
                mach.work(job)
                gene = Gene(gene_id, job, mach)
                instance.chromo.setChromo(gene.getGene())
                gene_id += 1
                sch_list.append(
                    [mach.start_time, mach.avail_time, mach.id, cur.id, mach.setup_status, setup_time,dicision_point])  # 스케줄 리스트
                row_df = pd.DataFrame(sch_list, columns=sch_columns)
                row_df.transpose()
                df = pd.concat([df,row_df])

    return instance, mach_list, job_list, df


def check_avail(mach_list: list):  # 사용 가능한 머신 리스트인지 판단 -> 모든 셋업에 True가 포함 돼 있는지 확인 없다면 변경
    avail_check_list = np.array(
        [[1 if mach.avail_matrix[i] else 0 for i in range(STATUSNUM)] for mach in mach_list])
    avail_check_list2 = avail_check_list.sum(axis=0)

    if 0 in avail_check_list2:
        for i in range(STATUSNUM):
            if avail_check_list2[i] == 0:
                avail_check_list3 = avail_check_list.sum(axis=1)
                mach_id = np.where(avail_check_list3.any() <= (min(avail_check_list3)))
                mach = list(filter(lambda x: (x.id == (mach_id[0] + 1)), mach_list))
                mach[0].avail_matrix[i] = True

    return mach_list
