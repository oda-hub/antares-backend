__author__ = "Andrea Tramacere"


try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def get_targets_dic(targets_dic):
    target_names = [k for k in targets_dic if 'Tpname' in k]
    names_dict = {}
    target_names.sort()
    for ID, n in enumerate(target_names):
        l = [targets_dic[n]]
        if n.replace('pname', 'aname') in targets_dic:
            alias = targets_dic[n.replace('pname', 'aname')]
            if alias is not None:
                l.extend(targets_dic[n.replace('pname', 'aname')].split(';'))
        names_dict['src_%02d' % ID] = l

    return names_dict






