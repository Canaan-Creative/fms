<template>
    <Layout v-if="loaded" v-cloak>
        <div style="padding: 15px">
            {{$t('setting.RPi_module')}}
            <input
                    v-model="controller_module_value"
                    type="number"
                    min="0"
                    style="width: 80px; margin-right: 10px; margin-left: 15px"/>
            <Button size="small" type="success" @click="set_controller_module">{{$t('menu.change')}}</Button>
        </div>
        <div style="padding: 15px">
            {{$t('setting.RPi_mhs')}}
            <input
                    v-model="controller_mhs_value"
                    type="number"
                    min="0"
                    style="width: 80px; margin-right: 10px; margin-left: 15px"/>
            <Button size="small" type="success" @click="set_controller_mhs">{{$t('menu.change')}}</Button>
        </div>
        <div style="padding: 15px">
            {{$t('setting.temperature_threshold')}}
            <input
                    v-model="fan_temp_value"
                    type="number"
                    min="0"
                    style="width: 80px; margin-right: 10px; margin-left: 15px"/>
            <Button size="small" type="success" @click="set_fan_temp">{{$t('menu.change')}}</Button>
        </div>
        <div style="padding: 15px">
            {{$t('setting.collect_interval')}}
            <input
                    v-model="collect_interval_value"
                    type="number"
                    min="0"
                    style="width: 80px; margin-right: 10px; margin-left: 15px"/>
            <Button size="small" type="success" @click="set_collect_interval">{{$t('menu.change')}}</Button>
        </div>
        <Table size="small" :columns="column1" :data="data1"></Table>
        <Footer>
            <Button size="small" type="success" @click="modal1 = true">{{$t('menu.add')}}</Button>
            <Modal
                    v-model="modal1"
                    @on-ok="add">
                <Input
                        v-model="value"
                        placeholder="xxx.xxx.xxx.xxx ( - xxx.xxx.xxx.xxx)"
                        style="width: 300px"/>
            </Modal>
            <Button size="small" type="success" @click="clear">{{$t('menu.clear')}}</Button>
        </Footer>
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
                loaded: false,
                modal1: false,
                value: '',
                column1: [
                    {
                        title: 'IP',
                        key: 'ip'
                    },
                    {
                        title: 'Action',
                        key: 'led',
                        render: (h, params) => {
                            return h('i-button', {
                                props: {
                                    type: 'error',
                                    size: 'small'
                                },
                                on: {
                                    click: () => {
                                        var msg = this.loading();
                                        this.$store.dispatch('REMOVE_CONTROLLER', params.row.ip).then(
                                            () => {
                                                setTimeout(msg, 10)
                                            })
                                    }
                                }
                            }, this.$t('menu.delete'))
                        }
                    }
                ]
            }
        },
        methods: {
            set_controller_module() {
                var pref = this.$store.state.api.preferences.filter(pref => pref['pref_key'] === 'controller_module')[0]
                pref['pref_value'] = this.controller_module_value;
                this.$store.dispatch('SET_PREFERENCE', pref)
            },
            set_controller_mhs() {
                var pref = this.$store.state.api.preferences.filter(pref => pref['pref_key'] === 'mhs')[0];
                pref['pref_value'] = this.controller_mhs_value;
                this.$store.dispatch('SET_PREFERENCE', pref)
            },
            set_fan_temp() {
                var pref = this.$store.state.api.preferences.filter(pref => pref['pref_key'] === 'fan_temp')[0]
                pref['pref_value'] = this.fan_temp_value;
                this.$store.dispatch('SET_PREFERENCE', pref)
            },
            set_collect_interval() {
                var pref = this.$store.state.api.preferences.filter(pref => pref['pref_key'] === 'collect_interval')[0]
                pref['pref_value'] = this.collect_interval_value;
                this.$store.dispatch('SET_PREFERENCE', pref)
            },
            loading() {
                return this.$Message.loading({
                    content: 'Loading...',
                    duration: 0
                });
            },
            add() {
                var msg = this.loading();
                this.$store.dispatch('ADD_CONTROLLERS', this.value).then(
                    () => {
                        setTimeout(msg, 10)
                    })
            },
            clear() {
                var msg = this.loading();
                this.$store.dispatch('CLEAR_CONTROLLERS').then(
                    () => {
                        setTimeout(msg, 10)
                    })
            }
        },
        computed: {
            data1() {
                return this.$store.state.api.controllers
            }
        },
        mounted() {
            this.$store.dispatch('GET_CONTROLLERS').then(
                this.$store.dispatch('GET_PREFERENCES').then(
                    () => {
                        this.controller_module_value = this.$store.state.api.preferences.filter(pref => pref['pref_key'] === 'controller_module')[0]['pref_value'];
                        this.controller_mhs_value = this.$store.state.api.preferences.filter(pref => pref['pref_key'] === 'mhs')[0]['pref_value'];
                        this.fan_temp_value = this.$store.state.api.preferences.filter(pref => pref['pref_key'] === 'fan_temp')[0]['pref_value'];
                        this.collect_interval_value = this.$store.state.api.preferences.filter(pref => pref['pref_key'] === 'collect_interval')[0]['pref_value'];
                        this.loaded = true
                    }))
        }
    }
</script>
