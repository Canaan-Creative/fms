/* eslint-disable */
import axios from 'axios'

const state = {
    timestamp: '',
    controllers: [],
    datas: [],
    controllers_data: [],
    pools_data: [],
    devices_data: [],
    modules_data: [],
    preferences: [],
    sort: {},
    finished: false,
    data_keys: {
        pool_user: 'pool_user',
        pool_module: 'pool_module',
        controller_ip: 'controller_ip',
        controller_module: 'controller_module',
        controller_elapsed: 'controller_elapsed',
        controller_mhs: 'controller_mhs',
        controller_mhs_av: 'controller_mhs_av',
        module_fac0: 'module_fac0',
        module_fan_av: 'module_fan_av',
        module_max_temp: 'module_max_temp',
        module_vers: 'module_vers',
        ctrl_module_alert: 'ctrl_module_alert',
        ctrl_mhs_alert: 'ctrl_mhs_alert',
        temp_alert: 'temp_alert'
    }
}

var int2ip = (ip) => {
    return (ip >>> 24) + '.' +
        ((ip & 0x00ff0000) >>> 16) + '.' +
        ((ip & 0x0000ff00) >>> 8) + '.' +
        (ip & 0x000000ff)
}

const mutations = {
    API_START(state) {
        state.finished = false
    },
    API_FINISH(state) {
        state.finished = true
    },
    STORE_TIMESTAMP(state, timestamp) {
        state.timestamp = timestamp
    },
    STORE_CONTROLLERS(state, data) {
        state.controllers = data
    },
    STORE_DATAS(state, data) {
        state.datas = data
    },
    STORE_CONTROLLERS_DATA(state, data) {
        state.controllers_data = data
    },
    STORE_POOLS_DATA(state, data) {
        state.pools_data = data
    },
    STORE_DEVICES_DATA(state, data) {
        state.devices_data = data
    },
    STORE_MODULES_DATA(state, data) {
        state.modules_data = data
    },
    STORE_PREFERENCES(state, data) {
        state.preferences = data
    },
    STORE_SORT(state, data) {
        state.sort = data
    }
}

const getters = {
    getDatas: state => {
        var ip2Ctrl = {};
        for (var i = 0; i < state.controllers.length; i++) {
            ip2Ctrl[state.controllers[i].ip] = state.controllers[i];
        }
        var datas = [];
        for (var index in state.datas) {
            var data = state.datas[index];
            if (!ip2Ctrl[data[state.data_keys.controller_ip]]) {
                continue;
            }
            console.log('pref', state.preferences);
            if (state.preferences) {
                if (state.preferences.filter(pref => pref['pref_key'] === 'controller_module')[0]['pref_value'] > data[state.data_keys.controller_module]) {
                    data[state.data_keys.ctrl_module_alert] = true;
                }
                if (state.preferences.filter(pref => pref['pref_key'] === 'mhs')[0]['pref_value'] > data[state.data_keys.controller_mhs]) {
                    data[state.data_keys.ctrl_mhs_alert] = true;
                }
                if (state.preferences.filter(pref => pref['pref_key'] === 'fan_temp')[0]['pref_value'] < data[state.data_keys.module_max_temp]) {
                    data[state.data_keys.temp_alert] = true;
                }
            }

            if (data[state.data_keys.temp_alert] || data[state.data_keys.controller_mhs] || data[state.data_keys.ctrl_module_alert]) {
                datas.unshift(data);
            } else {
                datas.push(data);
            }
        }
        if (state.sort.key) {
            datas.sort(function (d1, d2) {
                var res;
                if (state.sort.key === state.data_keys.controller_ip) {
                    res = compareIp(d1[state.sort.key], d2[state.sort.key]);
                } else {
                    if (d1[state.sort.key] > d2[state.sort.key]) {
                        res = 1;
                    } else if (d1[state.sort.key] < d2[state.sort.key]) {
                        res = -1;
                    } else {
                        res = 0;
                    }
                }
                return res * (state.sort.asc ? 1 : -1);
            });
        }
        console.log('getDatas', datas);
        return datas
    },
};

function compareIp(ip1, ip2) {
    var str1 = ip1.split('.');
    var str2 = ip2.split('.');
    for (var i in str1) {
        if (str1[i] !== str2[i]) {
            var i1 = parseInt(str1[i]);
            var i2 = parseInt(str2[i]);
            return i1 > i2 ? 1 : -1;
        }
    }
    return 0;
}

function generateIfNewData(state, commit) {
    if (!state.controllers_data) {
        return;
    }
    var datas = generateDatas(state.modules_data, state.controllers_data, state.pools_data, state);
    commit('STORE_DATAS', datas);
    commit('STORE_CONTROLLERS_DATA', null);
    commit('STORE_POOLS_DATA', null);
    commit('STORE_DEVICES_DATA', null);
    commit('STORE_MODULES_DATA', null);
}

function generateDatas(modules_data, controllers_data, pools_data, state) {
    console.log('data: ', modules_data, controllers_data, pools_data);
    var ip2ModuleDatas = {};
    for (var i = 0; i < modules_data.length; i++) {
        var module_data = modules_data[i];
        var ip = module_data['ip'];
        if (!ip2ModuleDatas[ip]) {
            ip2ModuleDatas[ip] = [module_data];
        } else {
            ip2ModuleDatas[ip].push(module_data);
        }
    }
    var ip2CtrlData = {};
    for (var i = 0; i < controllers_data.length; i++) {
        var ctrl_data = controllers_data[i];
        var ip = ctrl_data['ip'];
        if (!ip2CtrlData[ip]) {
            ip2CtrlData[ip] = ctrl_data;
        }
    }
    var ip2PoolData = {};
    var user2Ips = {};
    var alive_pools_data = pools_data.filter(pool => pool.status === 'Alive');
    for (var i = 0; i < alive_pools_data.length; i++) {
        var ip = alive_pools_data[i]['ip'];
        if (!ip2PoolData[ip]) {
            var firstPoolData = alive_pools_data.filter(pool => pool.ip === ip)
                .sort(pool => pool.priority)[0]; // 只取第一个
            ip2PoolData[ip] = firstPoolData;
            if (!user2Ips[firstPoolData.user]) {
                user2Ips[firstPoolData.user] = [ip];
            } else {
                user2Ips[firstPoolData.user].push(ip);
            }
        }
    }

    var datas = [];
    for (ip in ip2ModuleDatas) {
        var data = {};
        var ctrl_module_datas = ip2ModuleDatas[ip];
        data[state.data_keys.module_fac0] = (ctrl_module_datas[0]['fac0']) ? ctrl_module_datas[0]['fac0'] : 0;
        var fan_sum = 0;
        var max_temp = 0;
        var vers = [];
        for (var i = 0; i < ctrl_module_datas.length; i++) {
            var temp_module = ctrl_module_datas[i];
            fan_sum += temp_module['fan'];
            max_temp = (max_temp < temp_module['temp']) ? temp_module['temp'] : max_temp;
            var cur_ver = temp_module['ver'].substring(0, 3);
            if (!vers.includes(cur_ver)) {
                vers.push(cur_ver);
            }
        }
        data[state.data_keys.module_fan_av] = Math.round(fan_sum / ctrl_module_datas.length);
        data[state.data_keys.module_max_temp] = max_temp;
        data[state.data_keys.module_vers] = vers.join(',');
        data[state.data_keys.controller_ip] = ip;

        var controller_data = ip2CtrlData[ip];
        console.log('controller: ', controller_data);
        if (!controller_data) {
            continue;
        }
        data[state.data_keys.controller_elapsed] = controller_data['elapsed'];
        data[state.data_keys.controller_mhs] = computeMhs(controller_data['mhs_av']);
        data[state.data_keys.controller_mhs_av] = computeMhs(controller_data['mhs_av']);
        data[state.data_keys.controller_module] = ctrl_module_datas.length;

        var pool_data = ip2PoolData[ip];
        console.log('pools: ', pool_data);
        if (!pool_data) {
            continue;
        }
        data[state.data_keys.pool_user] = pool_data['url'] + ' : ' + pool_data['user'];

        var ips = user2Ips[pool_data.user];
        console.log('ips: ', ips);
        var pool_module = 0;
        ips.forEach(ip => pool_module += ip2ModuleDatas[ip].length);
        data[state.data_keys.pool_module] = pool_module;

        datas.push(data);
    }
    return datas
}

function computeMhs(mhs) {
    return Math.floor(mhs / 1024 / 1024);
}

const actions = {
    SET_LED(context, data) {
        return axios.post('http://127.0.0.1:4139/led', {
            modules: data
        })
    },
    ADD_CONTROLLERS({commit, state}, ips) {
        console.log('ips: ', ips)
        var ctrls = [];
        for (var i = 0; i < state.controllers.length; i++) {
            ctrls.push(state.controllers[i]);
        }
        const re0 = /^([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$/
        const re1 = /^([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\s*-\s*([0-9]{1,3})$/
        const re2 = /^([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\s*-\s*([0-9]{1,3})\.([0-9]{1,3})$/
        const re3 = /^([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\s*-\s*([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$/
        const re4 = /^([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\s*-\s*([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$/
        var s, ip, i, ip0, ip1
        if (re0.test(ips)) {
            s = re0.exec(ips)
            for (i = 1; i <= 4; i++) {
                s[i] = parseInt(s[i])
                if (s[i] > 255) {
                    return
                }
            }
            ctrls.push({ip: ips})
        } else if (re1.test(ips)) {
            s = re1.exec(ips)
            for (i = 1; i <= 5; i++) {
                s[i] = parseInt(s[i])
                if (s[i] > 255) {
                    return
                }
            }
            ip0 = (((s[1] * 256) + s[2]) * 256 + s[3]) * 256 + s[4]
            ip1 = (((s[1] * 256) + s[2]) * 256 + s[3]) * 256 + s[5]
            for (ip = ip0; ip <= ip1; ip++) {
                ctrls.push({ip: int2ip(ip)})
            }
        } else if (re2.test(ips)) {
            s = re2.exec(ips)
            for (i = 1; i <= 6; i++) {
                s[i] = parseInt(s[i])
                if (s[i] > 255) {
                    return
                }
            }
            ip0 = (((s[1] * 256) + s[2]) * 256 + s[3]) * 256 + s[4]
            ip1 = (((s[1] * 256) + s[2]) * 256 + s[5]) * 256 + s[6]
            for (ip = ip0; ip <= ip1; ip++) {
                ctrls.push({ip: int2ip(ip)})
            }
        } else if (re3.test(ips)) {
            s = re3.exec(ips)
            for (i = 1; i <= 7; i++) {
                s[i] = parseInt(s[i])
                if (s[i] > 255) {
                    return
                }
            }
            ip0 = (((s[1] * 256) + s[2]) * 256 + s[3]) * 256 + s[4]
            ip1 = (((s[1] * 256) + s[5]) * 256 + s[6]) * 256 + s[7]
            for (ip = ip0; ip <= ip1; ip++) {
                ctrls.push({ip: int2ip(ip)})
            }
        } else if (re4.test(ips)) {
            s = re4.exec(ips)
            for (i = 1; i <= 8; i++) {
                s[i] = parseInt(s[i])
                if (s[i] > 255) {
                    return
                }
            }
            ip0 = (((s[1] * 256) + s[2]) * 256 + s[3]) * 256 + s[4]
            ip1 = (((s[5] * 256) + s[6]) * 256 + s[7]) * 256 + s[8]
            for (ip = ip0; ip <= ip1; ip++) {
                ctrls.push({ip: int2ip(ip)})
            }
        }

        return axios.post('http://127.0.0.1:4139/controllers', {
            controllers: ctrls
        }).then((response) => {
            commit('STORE_CONTROLLERS', response.data.result)
        }, (err) => {
            console.log(err)
        })
    },
    REMOVE_CONTROLLER({commit, state}, ip) {
        return axios.delete('http://127.0.0.1:4139/controllers/' + ip)
            .then((response) => {
                console.log('controllers: ', response.data.result)
                commit('STORE_CONTROLLERS', response.data.result)
            }, (err) => {
                console.log(err)
            })
    },
    CLEAR_CONTROLLERS({commit}) {
        return axios.post('http://127.0.0.1:4139/controllers', {
            controllers: []
        }).then((response) => {
            commit('STORE_CONTROLLERS', response.data.result)
        }, (err) => {
            console.log(err)
        })
    },
    GET_DATA({commit, state, dispatch}) {
        var ts = state.timestamp;
        dispatch('GET_TIMESTAMP').then((response) => {
            console.log('timestamp: ts ', state.timestamp, ts);
            if ((ts.timestamp !== state.timestamp.timestamp || ts.force_update === '1' || state.timestamp.force_update === '1')
                && state.timestamp.timestamp !== '0') {
                // commit('API_START');
                console.log('get data api');
                dispatch('GET_CONTROLLERS_DATA')
                    .then((response) => {
                        dispatch('GET_POOLS_DATA')
                    })
                    .then((response) => {
                        dispatch('GET_DEVICES_DATA')
                    })
                    .then((response) => {
                        dispatch('GET_MODULES_DATA')
                    })
                    .then((response) => {
                        commit('API_FINISH')
                    })
            }
        })
    },
    FORCE_GETDATA({commit, state, dispatch}) {
        commit('STORE_TIMESTAMP', '');
        dispatch('GET_DATA');
    },
    SET_SORT({commit, state}, data) {
        var sort = {'key': data, 'asc': true};
        if (data === state.sort.key) {
            sort.asc = !state.sort.asc;
        }
        commit('STORE_SORT', sort)
    },
    GET_TIMESTAMP({commit}) {
        return axios.get('http://127.0.0.1:4139/timestamp').then((response) => {
            commit('STORE_TIMESTAMP', response.data.result)
        }, (err) => {
            console.log(err)
        })
    },
    GET_CONTROLLERS({commit}) {
        return axios.get('http://127.0.0.1:4139/controllers').then((response) => {
            commit('STORE_CONTROLLERS', response.data.result)
        }, (err) => {
            console.log(err)
        })
    },
    GET_CONTROLLERS_DATA({commit}) {
        return axios.get('http://127.0.0.1:4139/controllers_data').then((response) => {
            commit('STORE_CONTROLLERS_DATA', response.data.result)
        }, (err) => {
            console.log(err)
        })
    },
    GET_POOLS_DATA({commit}) {
        return axios.get('http://127.0.0.1:4139/pools_data').then((response) => {
            commit('STORE_POOLS_DATA', response.data.result)
        }, (err) => {
            console.log(err)
        })
    },
    GET_DEVICES_DATA({commit}) {
        return axios.get('http://127.0.0.1:4139/devices_data').then((response) => {
            commit('STORE_DEVICES_DATA', response.data.result)
        }, (err) => {
            console.log(err)
        })
    },
    GET_MODULES_DATA({state, commit}) {
        return axios.get('http://127.0.0.1:4139/modules_data').then((response) => {
            commit('STORE_MODULES_DATA', response.data.result)
            generateIfNewData(state, commit);
        }, (err) => {
            console.log(err)
        })
    },
    GET_PREFERENCES({commit}) {
        return axios.get('http://127.0.0.1:4139/preferences').then((response) => {
            commit('STORE_PREFERENCES', response.data.result)
        }, (err) => {
            console.log(err)
        })
    },
    SET_PREFERENCE({commit}, pref) {
        return axios.post('http://127.0.0.1:4139/preference', {
            preference: pref
        }).then((response) => {
            commit('STORE_PREFERENCES', response.data.result)
        }, (err) => {
            console.log(err)
        })
    }
}

export default {
    state,
    mutations,
    actions,
    getters
}
