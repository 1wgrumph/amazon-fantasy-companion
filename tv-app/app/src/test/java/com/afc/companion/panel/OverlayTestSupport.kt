package com.afc.companion.panel

import java.io.File
import java.lang.reflect.InvocationTargetException
import com.afc.companion.ui.theme.productSource

// Resource group: none shared. Reflection keeps missing product APIs assertion-red, never compile-red.
internal fun overlayType(name: String): Class<*> = try {
    Class.forName("com.afc.companion.panel.$name")
} catch (missing: ClassNotFoundException) {
    throw AssertionError("Missing overlay API: $name in com.afc.companion.panel", missing)
}

internal fun overlayCall(target: Any, name: String, vararg args: Any): Any? {
    val method = target.javaClass.methods.singleOrNull { it.name == name && it.parameterCount == args.size }
        ?: throw AssertionError("Missing overlay API: ${target.javaClass.simpleName}.$name/${args.size}")
    return try {
        method.invoke(target, *args)
    } catch (failure: InvocationTargetException) {
        throw failure.targetException
    }
}

internal class OverlayHarness(var permitted: Boolean = true) {
    val panel = PanelController(listOf(TL), TL, false)
    var added = 0
    var removed = 0
    var permissionRequests = 0
    private val controller: Any by lazy {
        val type = overlayType("OverlayController")
        val constructor = type.constructors.singleOrNull {
            it.parameterTypes.toList() == listOf(PanelController::class.java) + List(4) { Function0::class.java }
        } ?: throw AssertionError(
            "Missing overlay API: OverlayController(panel, hasPermission: () -> Boolean, " +
                "requestPermission: () -> Unit, addWindow: () -> Unit, removeWindow: () -> Unit)",
        )
        constructor.newInstance(panel, { permitted }, { permissionRequests++; Unit }, { added++; Unit }, { removed++; Unit })
    }

    fun call(name: String): Any? = overlayCall(controller, name)
    fun sharedPanel(): PanelController = overlayCall(controller, "getPanel") as PanelController
}

internal fun overlaySource(path: String): String {
    val file = File(System.getProperty("afc.repoRoot"), "tv-app/app/src/main/java/com/afc/companion/$path")
    if (!file.isFile) throw AssertionError("Missing overlay integration: $path")
    return productSource(path)
}

internal fun overlayBox(width: Int, height: Int): Box {
    val geometry = checkNotNull(overlayType("OverlayGeometry").getField("INSTANCE").get(null))
    return overlayCall(geometry, "layout", width, height) as Box
}
