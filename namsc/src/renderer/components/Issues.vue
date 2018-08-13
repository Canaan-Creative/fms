<template>
    <Layout v-if="loaded">
        <table class="table table-bordered table-striped text-center">
            <thead>
            <tr>
                <th v-on:click="changeSort('pool_user')">{{$t('issue.pool_worker')}}</th>
                <th v-on:click="changeSort('pool_module')">{{$t('issue.pool_module')}}</th>
                <th v-on:click="changeSort('controller_ip')">{{$t('issue.RPi')}}({{this.controller_ip_num}})</th>
                <th v-on:click="changeSort('controller_module')">{{$t('issue.RPi_module')}}</th>
                <th v-on:click="changeSort('controller_elapsed')">{{$t('issue.elapsed')}}</th>
                <th v-on:click="changeSort('module_fac0')">{{$t('issue.fac')}}</th>
                <th v-on:click="changeSort('controller_mhs')">{{$t('issue.mhs')}}</th>
                <th v-on:click="changeSort('controller_mhs_av')">{{$t('issue.mhs_av')}}</th>
                <th v-on:click="changeSort('module_fan_av')">{{$t('issue.fan_av')}}</th>
                <th v-on:click="changeSort('module_max_temp')">{{$t('issue.temp')}}</th>
                <th v-on:click="changeSort('module_vers')">{{$t('issue.version')}}</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="data in data1">
                <td>{{data.pool_user}}</td>
                <td>{{data.pool_module}}</td>
                <td>
                    <Button size="small" type="text" @click="jumpToUrl(data)">{{data.controller_ip}}</Button>
                </td>
                <td v-bind:style="{'background': getCtrlModuleColor(data)}">{{data.controller_module}}</td>
                <td>{{formatTime(data.controller_elapsed)}}</td>
                <td>{{data.module_fac0}}</td>
                <td v-bind:style="{'background': getCtrlMhsColor(data)}">{{formatMhs(data.controller_mhs)}}</td>
                <td>{{formatMhs(data.controller_mhs_av)}}</td>
                <td>{{data.module_fan_av}}</td>
                <td v-bind:style="{'background': getTempColor(data)}">{{data.module_max_temp}}</td>
                <td>{{data.module_vers}}</td>
            </tr>
            </tbody>
        </table>
    </Layout>
    <Layout v-else>
        <Spin size="large"></Spin>
    </Layout>
</template>
<script>
    /* eslint-disable */
    export default {
        data() {
            return {
                controller_ip_num: 0,
            }
        },
        computed: {
            data1() {
                console.log('get data1 in issue');
                var data = this.$store.getters.getDatas;
                this.controller_ip_num = data.length;
                return data;
            },
            loaded() {
                console.log('loaded in issue', this.$store.state.api.finished);
                return this.$store.state.api.finished;
            }
        },
        created() {
            this.$store.dispatch('GET_CONTROLLERS').then();
            this.$store.dispatch('GET_PREFERENCES').then();
        },
        methods: {
            getCtrlModuleColor(data) {
                if (data.ctrl_module_alert) {
                    return "red";
                }
                return "transparent";
            },
            getCtrlMhsColor(data) {
                if (data.ctrl_mhs_alert) {
                    return "red";
                }
                return "transparent";
            },
            getTempColor(data) {
                if (data.temp_alert) {
                    return "red";
                }
                return "transparent";
            },
            formatTime(seconds) {
                var timeStr = seconds % 60 + 's';
                seconds = Math.floor(seconds / 60); // 分钟
                if (seconds > 0) {
                    timeStr = seconds % 60 + 'm ' + timeStr;
                    seconds = Math.floor(seconds / 60); // 小时
                    if (seconds > 0) {
                        timeStr = seconds % 24 + 'h ' + timeStr;
                        seconds = Math.floor(seconds / 24);
                        if (seconds > 0) {
                            timeStr = seconds + 'd ' + timeStr;
                        }
                    }
                }
                return timeStr;
            },
            formatMhs(mhs) {
                return mhs + 'T';
            },
            jumpToUrl(data) {
                console.log('jumpToUrl');
                window.open('http://' + data.controller_ip);
            },
            changeSort(data) {
                console.log('changeSort', data);
                this.$store.dispatch('SET_SORT', data);
            },
            loading() {
                return this.$Message.loading({
                    content: 'Loading...',
                    duration: 0
                });
            },
        }
    }
</script>
<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    tr, th {
        text-align: center;
        padding: 10px;
    }

    td {
        text-align: center;
        padding-left: 10px;
        padding-right: 10px;
    }

</style>