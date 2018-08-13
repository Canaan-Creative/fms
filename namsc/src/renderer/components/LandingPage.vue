<style scoped>
    .menu-item span {
        display: inline-block;
        overflow: hidden;
        width: 69px;
        text-overflow: ellipsis;
        white-space: nowrap;
        vertical-align: bottom;
        transition: width .2s ease .2s;
    }

    .menu-item i {
        transform: translateX(0px);
        transition: font-size .2s ease, transform .2s ease;
        vertical-align: middle;
        font-size: 16px;
    }

    .collapsed-menu span {
        width: 0px;
        transition: width .2s ease;
    }

    .collapsed-menu i {
        transform: translateX(5px);
        transition: font-size .2s ease .2s, transform .2s ease .2s;
        vertical-align: middle;
        font-size: 22px;
    }

    .languageButton {
        position: absolute;
        bottom: 5%;
    }
</style>
<template>
    <div class="layout">
        <Layout :style="{minHeight: '100vh'}">
            <Sider collapsible :collapsed-width="78" v-model="isCollapsed">
                <Menu active-name="issues" theme="dark" width="auto" :class="menuitemClasses" @on-select="jump">
                    <MenuItem name="issues">
                        <div>
                            <Icon type="information-circled"></Icon>
                            <span>&nbsp{{$t('menu.issue')}}</span>
                        </div>
                    </MenuItem>
                    <MenuItem name="settings">
                        <Icon type="settings"></Icon>
                        <span>{{$t('menu.setting')}}</span>
                    </MenuItem>
                </Menu>
                <Button class="languageButton" size="small" type="info" long @click="changeLanguage">{{$t('menu.language')}}</Button>
            </Sider>
            <router-view></router-view>
        </Layout>
    </div>
</template>
<script>
    /* eslint-disable */
    export default {
        data() {
            return {
                isCollapsed: true
            }
        },
        computed: {
            menuitemClasses: function () {
                return [
                    'menu-item',
                    this.isCollapsed ? 'collapsed-menu' : ''
                ]
            }
        },
        methods: {
            jump(name) {
                this.$router.push(name)
            },
            changeLanguage() {
                this.$i18n.locale === 'zh' ? this.$i18n.locale = 'en' : this.$i18n.locale = 'zh'
            }
        },
        mounted() {
            this.$router.push('issues')
        }
    }
</script>
