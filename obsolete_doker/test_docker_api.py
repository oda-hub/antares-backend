import docker

image='root-c7'
mm_exec='/mnt/antares_bin/multiMessenger'
#        /mnt/antares_bin/multiMessenger
dec=23
ra=86
index_min = 2 
index_max = 3
roi= 1
root_env='/Users/orion/astro/Programmi/Projects/Active/CDCI_DATA_ANALYSIS/antares-backend/antares_environment/'
#         /Users/orion/astro/Programmi/Projects/Active/CDCI_DATA_ANALYSIS/antares-backend/antares_environment
docker_mnt_point='/mnt'
#                 /mnt
out_dir='antares_output'


dec=23
ra=86
index_min = 2 
index_max = 3
roi= 1
file='1sdasdasasdsa_ra%f2.2_dec%f2.2_ul.txt'%(ra,dec)


exec_cmd='%s %f %f %f %f %f %s %s %s'%(mm_exec,dec, ra, index_min, index_max, roi, docker_mnt_point,out_dir, file)
print('cmd',exec_cmd)

client = docker.from_env()
c=client.containers.run(image, exec_cmd,volumes={root_env:{'bind':docker_mnt_point,'mode':'rw'}},detach=True)
c.logs()