import { useTranslation } from "react-i18next"
import styles from "./InteractionsLimit.module.css"
import Logo from "../../assets/logo-mre.jpg"

export const InteractionsLimitPage = () => {
    const { t, i18n } = useTranslation()

    return (
        <section className={styles.limitPageContainer}>
            <div className={styles.limitPage}>
                <img src={Logo} alt="Logo de Ministerio de Relaciones Exteriores"></img>
                <h4 className={styles.chatEmptyStateSubtitle}>{t("interactionsLimitTitle")}</h4>
            </div>
        </section>
    )
}
